def get_ewkt_from_pointlist(pointlist):
	s = 'SRID=28992;POLYGON(('
	s += ', '.join( str(p[0])+' '+str(p[1]) for p in pointlist )
	s+= '))'
	return s

def get_ewkt_from_bounds(x_min, y_min, x_max, y_max):
    return 'SRID=28992;POLYGON(({0} {1}, {2} {1}, {2} {3}, {0} {3}, {0} {1}))'.format(x_min, y_min, x_max, y_max)