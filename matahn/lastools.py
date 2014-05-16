import subprocess32 as subprocess
from matahn import app

def lasmerge(filenames, x_min, y_min, x_max, y_max, outname):
	q = [app.config['LASMERGE_BINARY'], '-inside', x_min, y_min, x_max, y_max, '-olaz', outname, '-i'] + filenames
	subprocess.call(q)
	return outname

def lasinfotxt(filename):
	subprocess.call([app.config['LASINFO_BINARY'], filename, '-otxt'])
	return filename[:-3]+'txt'

