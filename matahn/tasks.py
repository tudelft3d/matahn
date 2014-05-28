from celery import Celery

import smtplib
from email.mime.text import MIMEText

from matahn import app
from matahn.database import db_session
from matahn.models import Tile
from matahn.lastools import lasmerge
from matahn.util import get_ewkt_from_bounds


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

@celery_app.task
def new_task(left, bottom, right, top, ahn2_class, emailto, task_id=None):
    if ahn2_class == 'ug': ahn2_class = 'u|g'
    ewkt = get_ewkt_from_bounds(left, bottom, right, top)
    filenames = db_session.query(Tile.path).filter(Tile.ahn2_class.match(ahn2_class)).filter(Tile.geom.intersects(ewkt)).all()
    filenames = [f[0] for f in filenames]
    output_laz = app.config['RESULTS_FOLDER'] + str(new_task.request.id)+'.laz'
    lasmerge(filenames, left, bottom, right, top, output_laz)
    return {'downloadlink': str(new_task.request.id), 'emailto': emailto}
    # return {'filename': str(new_task.request.id)+'.laz', 'ahn2_class': ahn2_class, 'geom': ewkt}


@celery_app.task
def sendemail(o): #-- o is the object returned by new_task(), it is automagically passed by Celery's chain
  sender = '***REMOVED***'
  receiver = o['emailto']
  core = """
  Greetings, 

  your AHN2 file is ready to be downloaded: http://3dsm.bk.tudelft.nl/matahn/tasks/%s

  Notice that we keep the file on our server only for 24h.

  Cheers,
  the MATAHN team
  http://3dsm.bk.tudelft.nl/matahn
  """ % (o['downloadlink'])
  msg = MIMEText(core)
  msg['Subject'] = 'Your AHN2 file is ready'
  msg['From'] = sender
  msg['To'] = receiver
  # s = smtplib.SMTP_SSL('smtp-a.tudelft.nl')
  # s.login('hledoux', '***REMOVED***')
  s = smtplib.SMTP_SSL('***REMOVED***')
  s.login('***REMOVED***', '***REMOVED***')
  s.sendmail(sender, [receiver], msg.as_string())
  s.quit()
