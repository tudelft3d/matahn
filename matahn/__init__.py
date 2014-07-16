from flask import Flask

class default_settings(object):
    DEBUG = False
    
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

    TRUSTED_IP_ADDRESSES = ['127.0.0.1']


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