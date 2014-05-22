from flask import Flask

app = Flask(__name__, static_url_path='')
app.config.from_object('matahn.default_settings')
app.config.from_envvar('MATAHN_SETTINGS')

import matahn.views
import matahn.models

from matahn.database import db_session
from matahn.tasks import celery_app

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()