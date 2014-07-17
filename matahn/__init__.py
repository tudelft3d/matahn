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