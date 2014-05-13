from sqlalchemy import create_engine

engine = create_engine('postgresql://ravi@localhost/testpy', echo=True)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from geoalchemy2 import Geometry

Base = declarative_base()

class Tile(Base):
    __tablename__ = 'tiles'
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    active = Column(Boolean)
    pointcount = Column(Integer)
    ahn2_type = String()
    geom = Column(Geometry('POLYGON', srid=28992))

def create_table():
	Tile.__table__.create(engine)
def drop_table():
	Tile.__table__.drop(engine)


def load_tile_from_file(filename):
	info_txt = generate_lasinfotxt(filename)
	info_dict = read_lasinfotxt(info_txt)

	if filename.startswith('u'):
		ahn2_type = 'uitgefilterd'
	elif filename.startswith('g'):
		ahn2_type = 'gefilterd'

	x_max, y_max, z_max = info_dict['max_xyz']
	x_min, y_min, z_min = info_dict['min_xyz']
	wkt = 'POLYGON(({0} {1}, {2} {1}, {2} {3}, {0} {3}, {0} {1}))'.format(x_min, y_min, x_max, y_max)

	tile = Tile(filename=filename, active=True, pointcount=info_dict['pointcount'], ahn2_type=ahn2_type, geom=wkt)

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

import subprocess32 as subprocess
LASINFO_BINARY = '/usr/local/bin/lasinfo_lastools'
def generate_lasinfotxt(filename):
	subprocess.call([LASINFO_BINARY, filename, '-otxt'])
	return filename[:-3]+'txt'