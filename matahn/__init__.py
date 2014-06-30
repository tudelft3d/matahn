from flask import Flask

class default_settings(object):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://matahn:matahn@localhost/matahn'
    RESULTS_FOLDER 	= '/data/matahn/results/'
    BLADINDEX_JSON = '/var/www/webahn/tiles.json'
    LASINFO_BINARY = '/usr/local/bin/lasinfo'
    LASMERGE_BINARY = '/usr/local/bin/lasmerge'
    CELERY_BROKER_URL = 'redis://localhost:6379/0',
    CELERY_RESULT_BACKEND = 'db+'+SQLALCHEMY_DATABASE_URI
    
    SERVER_NAME = '3dsm.bk.tudelft.nl'
    STATIC_DOWNLOAD_URL = '/matahn/tasks/download/'
    MAX_POINT_QUERY_SIZE = 400e6
    
    from celery.schedules import crontab
    CELERY_IMPORTS = ("matahn.tasks", )
    CELERYBEAT_SCHEDULE = {
    'rm-old-task-files': {
        'task': 'matahn.tasks.remove_old_laz_files',
        'schedule': crontab(hour=1, minute=1)
        }
    }
    CELERY_TIMEZONE = 'Europe/Amsterdam'
    MAX_HOURS = 24

    TRUSTED_IP_ADDRESSES = ['131.180.101.65', '127.0.0.1']


app = Flask(__name__, static_url_path='/static')
app.config.from_object(default_settings)
app.config.from_envvar('MATAHN_SETTINGS', silent=True)

import matahn.views
import matahn.models
import matahn.tasks

from matahn.database import db_session
from matahn.tasks import celery_app

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()