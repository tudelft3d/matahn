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

from flask import render_template, url_for, current_app
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
import sqlalchemy.types as types
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

import matahn
from matahn import app
from matahn.database import Base

lasclass_lookup = {
0:'Created, never classified',
1:'Unclassified',
2:'Ground', 
3:'Low Vegetation',
4:'Medium Vegetation',
5:'High Vegetation',
6:'building', 
7:'Low Point (noise)',
8:'Model Key-point (mass point)',
9:'Water', 
12:'Overlap Points',
26:'Artefact'}

class ClassificationsType(types.TypeDecorator):
    impl = String

    def __init__(self, length=None, **kwargs):
        super(ClassificationsType, self).__init__(length, **kwargs)

    def process_bind_param(self, value, dialect):
        if type(value) is list:
            return ",".join([str(c) for c in value])
        else:
            return value

    def process_result_value(self, value, dialect):
        return [int(c) for c in value.split(',')]

class Dataset(Base):
    __tablename__ = 'datasets'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    classes = Column(ClassificationsType(50)) # a comma separated list of ASPRS LAS classification codes that are available for this dataset

    def __repr__(self):
        return "Dataset {} [{}]".format(self.name, self.classes)

    def get_classes_with_names(self):
        return [(c, lasclass_lookup[c]) for c in self.classes]


class Tile(Base):
    __tablename__ = 'tiles'
    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True)
    name = Column(String(50))
    active = Column(Boolean)
    pointcount = Column(Integer)
    geom = Column(Geometry('POLYGON', srid=28992))
    
    dataset_id = Column(Integer, ForeignKey('datasets.id'))
    dataset = relationship('Dataset', backref='tiles')

    def __repr__(self):
    	return "Tile {} [{}]".format(self.name, self.dataset.name)

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(String, primary_key=True)
    classes = Column(ClassificationsType(50))
    emailto = Column(String)
    ip_address = Column(String)
    time_stamp = Column(DateTime)
    geom = Column(Geometry('POLYGON', srid=28992))
    log_execution_time = Column(Float)
    log_actual_point_count = Column(Integer)

    dataset_id = Column(Integer, ForeignKey('datasets.id'))
    dataset = relationship('Dataset', backref='tasks')

    def __repr__(self):
        return "task {}".format(self.id)

    def get_status(self):
        async_result = matahn.tasks.new_task.AsyncResult(self.id)
        return async_result.status

    def get_filename(self):
        return self.id + '.laz'

    def get_absolute_path(self):
        return app.config['RESULTS_FOLDER'] + self.get_filename()

    def get_relative_url(self):
        return app.config['STATIC_DOWNLOAD_URL'] + self.get_filename()

    # def relaunch(self):
    #     # new celery task
    #     result = matahn.tasks.new_task.apply_async((left, bottom, right, top, classification))
    #     # store task parameters in db
    #     task = Task(id=result.id, ahn2_class=self.ahn2_class, emailto=self.emailto, geom=get_ewkt_from_bounds(left, bottom, right, top) )
    #     db_session.add(task)
    #     db_session.commit()
    #     return task

    def send_email(self):
        import smtplib
        from email.mime.text import MIMEText

        # with app.app_context():
        receiver = self.emailto
        base_url = 'http://'+app.config['SERVER_NAME']+app.config['SERVER_LOCATION']
        body = render_template('mail_download_notification.html', 
            task_url=base_url+'/tasks/'+self.id,
            base_url=base_url
            )
        msg = MIMEText(body)
        msg['Subject'] = 'Your point cloud file is ready'
        msg['From'] = app.config['MAIL_FROM']
        msg['To'] = receiver
        
        s = smtplib.SMTP( app.config['MAIL_SERVER'], app.config['MAIL_PORT'] )
        s.starttls()
        s.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        s.sendmail(app.config['MAIL_FROM'], [receiver], msg.as_string())
        s.quit()

    def get_classes_with_names(self):
        return [(c, lasclass_lookup[c]) for c in self.classes]

    def get_classnames(self):
        return [lasclass_lookup[c] for c in self.classes]

    def __repr__(self):
        return "Task #{} [{}]".format(self.id, self.dataset.name)
