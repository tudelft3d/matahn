import smtplib
from email.mime.text import MIMEText

sender = 'h.ledoux@tudelft.nl'
receiver = 'hledouxtud@gmail.com'
lorem = 'allo les amis.\nEverything good?'
msg = MIMEText(lorem)
msg['Subject'] = 'Testing 1 2 testing'
msg['From'] = sender
msg['To'] = receiver

s = smtplib.SMTP_SSL('smtp-a.tudelft.nl')
s.login('hledoux', '')
s.sendmail(sender, [receiver], msg.as_string())
s.quit()

print "email sent."