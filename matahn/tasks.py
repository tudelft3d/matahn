from celery import Celery

from matahn import app
from matahn.database import db_session
from matahn.models import Tile, Task
from matahn.lastools import lasmerge
from matahn.util import get_geojson_from_bounds, get_ewkt_from_bounds


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
    lasmerge(filenames, left, bottom, right, top, output_laz)

    t = db_session.query(Task).filter(Task.id==str(new_task.request.id)).one()
    t.send_email()