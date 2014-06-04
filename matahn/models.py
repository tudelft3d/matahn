from sqlalchemy import Column, Integer, String, Boolean
from geoalchemy2 import Geometry

from matahn.database import Base

class Tile(Base):
    __tablename__ = 'tiles'
    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True)
    ahn2_bladnr = Column(String(5))
    ahn2_class = Column(String(1))
    active = Column(Boolean)
    pointcount = Column(Integer)
    geom = Column(Geometry('POLYGON', srid=28992))

    def __repr__(self):
    	return "tile {}_{}".format(self.ahn2_bladnr, self.ahn2_class)

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(String, primary_key=True)
    ahn2_class = Column(String(2))
    emailto = Column(String)
    geom = Column(Geometry('POLYGON', srid=28992))

    def __repr__(self):
        return "task {}".format(self.uuid)