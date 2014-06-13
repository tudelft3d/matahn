from flask import render_template, url_for
from sqlalchemy import Column, Integer, String, Boolean, Float
from geoalchemy2 import Geometry

import matahn
from matahn import app
from matahn.database import Base

class Tile(Base):
    __tablename__ = 'tiles'
    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True)
    ahn2_bladnr = Column(String(5))
    ahn2_class = Column(String(1))
    active = Column(Boolean)
    pointcount = Column(Integer)
    geom = Column(Geometry('POLYGON', srid=28992))

    def __repr__(self):
    	return "tile {}_{}".format(self.ahn2_bladnr, self.ahn2_class)

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(String, primary_key=True)
    ahn2_class = Column(String(2))
    emailto = Column(String)
    geom = Column(Geometry('POLYGON', srid=28992))
    log_execution_time = Column(Float)
    log_actual_point_count = Column(Integer)

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

        sender = '***REMOVED***'
        receiver = self.emailto
        body = render_template('mail_download_notification.html', task_url='http://'+app.config['SERVER_NAME']+'/matahn/tasks/'+self.id)
        msg = MIMEText(body)
        msg['Subject'] = 'Your AHN2 file is ready'
        msg['From'] = sender
        msg['To'] = receiver
        
        s = smtplib.SMTP_SSL( app.config['MAIL_SERVER'] )
        s.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        s.sendmail(sender, [receiver], msg.as_string())
        s.quit()