import subprocess32 as subprocess

# LASINFO_BINARY = '/usr/local/bin/lasinfo_lastools'
# LASMERGE_BINARY = '/usr/local/bin/lasmerge_lastools'
LASINFO_BINARY  = '/Users/hugo/software/lastools/bin/lasinfo'
LASMERGE_BINARY = 'lasmerge'

def lasmerge(filenames, x_min, y_min, x_max, y_max, outname):
	q = [LASMERGE_BINARY, '-inside', x_min, y_min, x_max, y_max, '-olaz', outname, '-i'] + filenames
	subprocess.call(q)
	return outname

def lasinfotxt(filename):
  # subprocess.call([LASINFO_BINARY, filename, '-otxt'])
	subprocess.call(['wine', LASINFO_BINARY, filename, '-otxt'])
	return filename[:-3]+'txt'

