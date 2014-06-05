from sqlalchemy import Column, Integer, String, Boolean
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

    def __repr__(self):
        return "task {}".format(self.uuid)

    def get_status(self):
        async_result = matahn.tasks.new_task.AsyncResult(self.id)
        return async_result.status

    def get_filename(self):
        return self.id + '.laz'

    def get_relative_url(self):
        return app.config['STATIC_DOWNLOAD_URL'] + self.get_filename()

    def send_email(self):
        import smtplib
        from email.mime.text import MIMEText

        sender = '***REMOVED***'
        receiver = self.emailto
        core = """
        Greetings AHN2-enthusiast, 

        your file is ready to be downloaded: http://3dsm.bk.tudelft.nl%s

        Notice that we keep the file on our server only for 24h.

        Cheers,
        the MATAHN team
        http://3dsm.bk.tudelft.nl/matahn
        """ % (self.get_relative_url())
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