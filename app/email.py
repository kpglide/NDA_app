from flask import current_app, render_template
from flask.ext.mail import Message
from . import mail

#Emails copy of blank NDA to recipient.  Also sends a copy to the app user. 
def send_nda_email(to, copy, subject, template, **kwargs):
	app = current_app._get_current_object()
	msg = Message(subject, sender=app.config['MAIL_SENDER'], recipients=to, cc=copy)
	msg.body = render_template(template + '.txt', **kwargs)
	msg.html = render_template(template + '.html', **kwargs)
	mail.send(msg)