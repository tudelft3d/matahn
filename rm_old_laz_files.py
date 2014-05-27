
# crontab -e
# 01 01 * * * /usr/local/bin/python /path/to/rm_old_laz_files.py
# every day at 1:01am the files will be deleted

import os
import time
import glob

MAX_HOURS = 24 #-- will remove files older than 24h
RESULTS_FOLDER = "/Users/hugo/www/webahn/results/"

for f in glob.glob(os.path.join(RESULTS_FOLDER, '*.laz')):
    if time.time() - os.path.getmtime(f) > (MAX_HOURS * 60 * 60): #-- older than 1h
        os.remove(f)
        print "file", f, "deleted."

