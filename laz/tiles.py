POSTGIS_CONNECTIONSTRING = 'postgresql://ravi@localhost/testpy'

from sqlalchemy import create_engine
engine = create_engine(POSTGIS_CONNECTIONSTRING, echo=True)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from geoalchemy2 import Geometry

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)

Base = declarative_base()

## General db stuff:

class Tile(Base):
    __tablename__ = 'tiles'
    id = Column(Integer, primary_key=True)
    filename = Column(String, unique=True)
    active = Column(Boolean)
    pointcount = Column(Integer)
    ahn2_type = String()
    geom = Column(Geometry('POLYGON', srid=28992))

    def __repr__(self):
    	return "tile<{}>".format(self.filename)

def create_table():
	Tile.__table__.create(engine)
def drop_table():
	Tile.__table__.drop(engine)

def get_tiles_from_bounds(session, x_min, y_min, x_max, y_max):
	ewkt = get_ewkt_from_bounds(x_min, y_min, x_max, y_max)
	tiles = session.query(Tile).filter(Tile.geom.ST_Intersects(ewkt)).all()

	return tiles

def get_ewkt_from_bounds(x_min, y_min, x_max, y_max):
	return 'SRID=28992;POLYGON(({0} {1}, {2} {1}, {2} {3}, {0} {3}, {0} {1}))'.format(x_min, y_min, x_max, y_max)


#### Stuff to import tiles from file to db:

import glob
def load_tiles_into_db(session, glob_expression):
	tile_files = glob.glob(glob_expression)

	tiles = []
	for tile_file in tile_files:
		t = get_tile_from_file(tile_file)
		tiles.append(t)

	session.add_all(tiles)
	session.commit()

from lastools import *
def get_tile_from_file(filename):
	info_txt = lasinfotxt(filename)
	info_dict = read_lasinfotxt(lasinfo_txt)

	if filename.startswith('u'):
		ahn2_type = 'uitgefilterd'
	elif filename.startswith('g'):
		ahn2_type = 'gefilterd'

	x_max, y_max, z_max = info_dict['max_xyz']
	x_min, y_min, z_min = info_dict['min_xyz']
	ewkt = get_ewkt_from_bounds(x_min, y_min, x_max, y_max)

	tile = Tile(filename=filename, active=True, pointcount=info_dict['pointcount'], ahn2_type=ahn2_type, geom=ewkt)

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


def example_usage():
	# assume you set up a postgis db that is specified in the POSTGIS_CONNECTIONSTRING
	# creating tiles table:
	create_table()
	
	# create session object for db interaction
	session = Session()

	# import laz files into tiles table:
	load_tiles_into_db(session, '/some/dir/*.laz')

	# get tiles
	tiles = get_tiles_from_bounds(session, 31000.0, 391250.0, 31005.0, 391255.0)

	# close db session when done interacting with db
	session.close()

	# access data like that:
	for tile in tiles:
		print tile.filename, tile.pointcount
	
	