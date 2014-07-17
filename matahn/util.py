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

def get_ewkt_from_pointlist(pointlist):
	s = 'SRID=28992;POLYGON(('
	s += ', '.join( str(p[0])+' '+str(p[1]) for p in pointlist )
	s+= '))'
	return s

def get_ewkt_from_bounds(x_min, y_min, x_max, y_max):
    return 'SRID=28992;POLYGON(({0} {1}, {2} {1}, {2} {3}, {0} {3}, {0} {1}))'.format(x_min, y_min, x_max, y_max)

def get_geojson_from_bounds(x_min, y_min, x_max, y_max):
	b=[x_min, y_min, x_max, y_max]
	return {"type":"Polygon","coordinates":[[[b[0], b[1]], [b[2], b[1]], [b[2], b[3]], [b[0], b[3]], [b[0], b[1]]]]}