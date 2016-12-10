# This file is part of MATAHN.

# MATAHN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# MATAHN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with MATAHN.  If not, see <http://www.gnu.org/licenses/>.

# Copyright 2014 Ravi Peters, Hugo Ledoux

#### Stuff to import tiles from file to db:
import glob
import os.path
import json

from matahn import app
from matahn.models import Tile
from matahn.database import db_session
from matahn.lastools import *
from matahn.util import get_ewkt_from_bounds, get_ewkt_from_pointlist

from sqlalchemy import func

def merge_tiles_from_taskfile(taskfile):
	with open(taskfile) as f:
		left = float(f.readline().split(':')[-1])
		bottom = float(f.readline().split(':')[-1])
		right = float(f.readline().split(':')[-1])
		top = float(f.readline().split(':')[-1])
		ahn2_class = f.readline().split(':')[-1].strip()

	if ahn2_class == 'ug': ahn2_class = 'u|g'
	ewkt = get_ewkt_from_bounds(left, bottom, right, top)
	filenames = db_session.query(Tile.path).filter(Tile.ahn2_class.match(ahn2_class)).filter(Tile.geom.intersects(ewkt)).all()
	filenames = [f[0] for f in filenames]

	lasmerge(filenames, left, bottom, right, top, taskfile[:-3]+'laz')

def load_tiles_into_db(dataset, glob_expression, bounds=None):
	tile_files = glob.glob(glob_expression)

	tiles = []
	for tile_file in tile_files:
		t = get_tile_from_file(tile_file, bounds)
		t.dataset = dataset
		tiles.append(t)

	db_session.add_all(tiles)
	db_session.commit()

def get_tile_from_file(path, bounds=None):
	
	lasinfo_file = path[:-3]+'txt'
	if os.path.isfile(lasinfo_file):
		info_txt = lasinfo_file 
	else:
		info_txt = lasinfotxt(path)

	info_dict = read_lasinfotxt(info_txt)

	filename = os.path.basename(path)
	name = filename.split('.')[0]

	if bounds is None:
		x_max, y_max, z_max = info_dict['max_xyz']
		x_min, y_min, z_min = info_dict['min_xyz']
		ewkt = get_ewkt_from_bounds(x_min, y_min, x_max, y_max)
	else:
		try:
			ewkt = get_ewkt_from_pointlist( bounds[name] )
		except:
			x_max, y_max, z_max = info_dict['max_xyz']
			x_min, y_min, z_min = info_dict['min_xyz']
			ewkt = get_ewkt_from_bounds(x_min, y_min, x_max, y_max)
	
	tile = Tile(path=path, active=True, pointcount=info_dict['pointcount'], name=name, geom=ewkt)

	return tile

def read_lasinfotxt(filename):
	result = {}
	with open(filename) as f:
		for line in f:
			if line.startswith('  number of point records'):
				result['pointcount'] = int(line.split()[-1])
			elif line.startswith('  min x y z:'):
				result['min_xyz'] = [ float(v) for v in line.split()[-3:] ]
			elif line.startswith('  max x y z:'):
				result['max_xyz'] = [ float(v) for v in line.split()[-3:] ]

	return result
	
