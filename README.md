MATAHN
=====

Download tool for AHN2 that delivers a LAZ file with the points inside a bounding box drawn by the user. Based on Flask and Openlayers 2.

Running
------
From project root:

`pip install -r requirements.txt`

`cp example_matahn.cfg matahn.cfg` and edit it

`export MATAHN_SETTINGS=/path/to/matahn.cfg`

Now these processes all need to be started in this order:

`reddis-server`

`celery -A matahn.celery_app worker`

`python runserver.py`

And make sure postgresql is running as wel

Preparing laz files
------
in dir with laz files:

`lasinfo -nc -nv -nmm -otxt -i *.laz`

`lasindex -append -i *.laz`

Importing tiles into DB
------
in (i)python shell

`from matahn.tile_io import load_tiles_into_db`

`load_tiles_into_db('/path/to/*.laz')`

Setting up reddis (for celery job handling)
------

just install with apt-get/brew

Postgresql
------
a database is required with postgis extension enabled 
