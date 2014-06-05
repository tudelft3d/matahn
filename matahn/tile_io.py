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

with open(app.config['BLADINDEX_JSON']) as f:
	BLADINDEX = json.load(f)


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

def load_tiles_into_db(glob_expression):
	tile_files = glob.glob(glob_expression)

	tiles = []
	for tile_file in tile_files:
		t = get_tile_from_file(tile_file)
		tiles.append(t)

	db_session.add_all(tiles)
	db_session.commit()

def get_tile_from_file(path):
	
	lasinfo_file = path[:-3]+'txt'
	if os.path.isfile(lasinfo_file):
		info_txt = lasinfo_file 
	else:
		info_txt = lasinfotxt(path)

	info_dict = read_lasinfotxt(info_txt)

	filename = os.path.basename(path)
	ahn2_class = filename[0]
	ahn2_bladnr = filename[1:6]

	ewkt = get_ewkt_from_pointlist( BLADINDEX[ahn2_bladnr] )

	tile = Tile(path=path, active=True, pointcount=info_dict['pointcount'], ahn2_bladnr=ahn2_bladnr, ahn2_class=ahn2_class, geom=ewkt)

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
	