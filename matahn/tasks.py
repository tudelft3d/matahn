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

from celery import Celery

from matahn import app
from matahn.database import db_session
from matahn.models import Tile, Task
from matahn import lastools
from matahn import tile_io
from matahn.util import get_geojson_from_bounds, get_ewkt_from_bounds

import os, glob, time

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery_app = make_celery(app)

@celery_app.task()
def new_task(left, bottom, right, top, ahn2_class):
    if ahn2_class == 'ug': ahn2_class = 'u|g'
    ewkt = get_ewkt_from_bounds(left, bottom, right, top)
    # geojson = get_geojson_from_bounds(left, bottom, right, top)
    filenames = db_session.query(Tile.path).filter(Tile.ahn2_class.match(ahn2_class)).filter(Tile.geom.intersects(ewkt)).all()
    filenames = [f[0] for f in filenames]
    
    output_laz = app.config['RESULTS_FOLDER'] + str(new_task.request.id)+'.laz'
    # this will cause an exception if something goes wrong while calling lasmerge executable
    t0 = time.time()
    lastools.lasmerge(filenames, left, bottom, right, top, output_laz)
    t1 = time.time()

    t = db_session.query(Task).filter(Task.id==str(new_task.request.id)).one()
    try:
        t.send_email()
    except:
        pass

    infotxt = lastools.lasinfotxt(output_laz)
    info = tile_io.read_lasinfotxt(infotxt)

    t.log_execution_time = t1-t0
    t.log_actual_point_count = info['pointcount']
    db_session.commit()

    # could also use this to do the mailing http://stackoverflow.com/questions/12526606/callback-for-celery-apply-async

@celery_app.task()
def remove_old_laz_files():
    for f in glob.glob(os.path.join(app.config['RESULTS_FOLDER'], '*')):
        if time.time() - os.path.getmtime(f) > (app.config['MAX_HOURS'] * 60 * 60): #-- older than 1h
            os.remove(f)
            print "file", f, "deleted."