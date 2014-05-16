#### Stuff to import tiles from file to db:
import glob
import os.path
import json

from matahn import app
from matahn.models import Tile
from matahn.database import db_session
from matahn.lastools import *

with open(app.config['BLADINDEX_JSON']) as f:
	BLADINDEX = json.load(f)


def get_ewkt_from_bounds(x_min, y_min, x_max, y_max):
	return 'SRID=28992;POLYGON(({0} {1}, {2} {1}, {2} {3}, {0} {3}, {0} {1}))'.format(x_min, y_min, x_max, y_max)

def get_ewkt_from_pointlist(pointlist):
	s = 'SRID=28992;POLYGON(('
	s += ', '.join( str(p[0])+' '+str(p[1]) for p in pointlist )
	s+= '))'
	return s

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
	if os.path.exists(lasinfo_file):
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