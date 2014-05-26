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
    
    DOWNLOAD_URL_PATH = '/matahn/download/'

app = Flask(__name__, static_url_path='/static')
# app.config.from_object(default_settings)
app.config.from_envvar('MATAHN_SETTINGS')

import matahn.views
import matahn.models

from matahn.database import db_session
from matahn.tasks import celery_app

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()