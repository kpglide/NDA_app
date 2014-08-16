import os
from flask import Flask, request, render_template, session, redirect, url_for
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import Required, Email, Length, Regexp
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Shell
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.mail import Mail, Message

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
#TODO For production, change secret key and move it to an environment variable
app.config['SECRET_KEY'] = 'development_key'
app.config['SQLALCHEMY_DATABASE_URI'] = \
	'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
manager = Manager(app)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

#Configure app to use Flask-Mail extension and Gmail for sending email
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_SENDER'] = 'TSports Legal Portal Admin <kpglide@gmail.com>'
mail = Mail(app)

#Forms
class LoginForm(Form):
	#TODO For production, consider updating email field validation to only accept
	#addresses from a specified domain
	email = TextField('Email Address', validators=[Required(), Email()])
	password = PasswordField('Password', validators=[Required(), Length(min=6, max=15)])
	submit = SubmitField('Log In')
	remember_me = BooleanField('Keep me logged in')

#Allows user to input contact info for the company to which the NDA form
#should be sent
class RecipientForm(Form):
	firstname = TextField("First Name", validators=[Required()])
	lastname = TextField("Last Name", validators=[Required()])
	email = TextField('Email Address', validators=[Required(), Email()])
	submit = SubmitField('Preview')

def us_states():
    """List of USA states.

    Return a list of ``(abbreviation, name)`` for all US states, sorted by name.
    Includes the District of Columbia.
    """
    # From http://www.usps.com/ncsc/lookups/abbreviations.html
    #Updated 2008-05-01
    return [
        ("AL", "Alabama"),
        ("AK", "Alaska"),
        ("AZ", "Arizona"),
        ("AR", "Arkansas"),
        ("CA", "California"),
        ("CO", "Colorado"),
        ("CT", "Connecticut"),
        ("DE", "Delaware"),
        ("DC", "District of Columbia"),
        ("FL", "Florida"),
        ("GA", "Georgia"),
        ("HI", "Hawaii"),
        ("ID", "Idaho"),
        ("IL", "Illinois"),
        ("IN", "Indiana"),
        ("IA", "Iowa"),
        ("KS", "Kansas"),
        ("KY", "Kentucky"),
        ("LA", "Louisiana"),
        ("ME", "Maine"),
        ("MD", "Maryland"),
        ("MA", "Massachusetts"),
        ("MI", "Michigan"),
        ("MN", "Minnesota"),
        ("MS", "Mississippi"),
        ("MO", "Missouri"),
        ("MT", "Montana"),
        ("NE", "Nebraska"),
        ("NV", "Nevada"),
        ("NH", "New Hampshire"),
        ("NJ", "New Jersey"),
        ("NM", "New Mexico"),
        ("NY", "New York"),
        ("NC", "North Carolina"),
        ("ND", "North Dakota"),
        ("OH", "Ohio"),
        ("OK", "Oklahoma"),
        ("OR", "Oregon"),
        ("PA", "Pennsylvania"),
        ("RI", "Rhode Island"),
        ("SC", "South Carolina"),
        ("SD", "South Dakota"),
        ("TN", "Tennessee"),
        ("TX", "Texas"),
        ("UT", "Utah"),
        ("VT", "Vermont"),
        ("VA", "Virginia"),
        ("WA", "Washington"),
        ("WV", "West Virginia"),
        ("WI", "Wisconsin"),
        ("WY", "Wyoming"),
        ]
	
class SignatoryForm(Form):
	state_choices = us_states()
	#TODO--NEED TO FIX CSS HERE SO THAT AN ERROR MESSAGE APPEARS WHEN
	#THIS BOX IS NOT CHECKED
	accept = BooleanField('''I am an authorized signatory of the company indicated below.  
							I agree to the terms of the Non-Disclosure Agreement above on 
							behalf of my company.''',
							validators=[Required()])
	company_name = TextField('Company Name (Full Legal Entity Name)', validators=[Required()])
	signatory_name = TextField('Your Name', validators=[Required()])
	signatory_title = TextField('Your Title', validators=[Required()])
	email = TextField('Email Address', validators=[Required(), Email()])
	company_address = TextField('Company Street Address', validators=[Required()])
	city = TextField('City', validators=[Required()])
	state = SelectField('State', choices=state_choices, validators=[Required()])
	zip_code = TextField('Zip or Postal Code', validators=[Required(), Regexp(u'^(\d{5}(-\d{4})?)$')])
	submit = SubmitField('I Agree') 
	
#Routes
@app.route('/', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		if form.password.data == 'testtest':
			session['email'] = form.email.data
			return redirect(url_for('home'))
		else:
			return redirect(url_for('login'))		
	return render_template('login.html', form=form, email=session.get('email'))

@app.route('/home')
def home():
	return render_template('home.html')
	
@app.route('/create_nda', methods=['GET', 'POST'])
def create_nda():
	form = RecipientForm()
	if form.validate_on_submit():
		session['recipient first name'] = form.firstname.data
		session['recipient last name'] = form.lastname.data
		session['party email'] = form.email.data
		return redirect(url_for('nda_preview'))
	else:
		return render_template('create_nda.html', form=form)

@app.route('/nda/<user_email>', methods=['GET', 'POST'])
def nda(user_email):
	f = open('static/Very Short NDA.txt', 'r')
	data = f.read().decode('utf-8') 
	paragraphs = data.split("\n\n")
	f.close()
	form = SignatoryForm()
	user_email = user_email
	if form.validate_on_submit():		
		party = NDA_Party(form.signatory_name.data, form.signatory_title.data,
							form.email.data, form.company_name.data, form.company_address.data,
							form.city.data, form.state.data, form.zip_code.data)
		#TODO: Use Flask-Moment to record click-through date
		#here as the NDA signature date
		db.session.add(party)
		send_nda_email([party.email], [user_email], 
						'Signed NDA for ' + party.signatory_name + '//' +
						party.company_name, 
						'mail/signed_nda', signatory_name=party.signatory_name, 
						user_email=user_email, company_name=party.company_name, 
						signatory_title=party.signatory_title, paragraphs=paragraphs,
						) 
		return redirect(url_for('thanks_for_signing'))
	return render_template('nda.html', user_email=user_email, paragraphs=paragraphs, form=form)
	
@app.route('/nda_preview')
def nda_preview():
	user_email = session.get('email')
	recipient_first_name = session.get('recipient first name')
	recipient_last_name = session.get('recipient last name')
	recipient_name = recipient_first_name + ' ' + recipient_last_name
	recipient_email = session.get('party email')
	return render_template('nda_preview.html', 
							recipient_name = recipient_name,
							recipient_email = recipient_email,
							user_email = user_email
							)
							
#Emails copy of blank NDA to recipient.  Also sends a copy to the app user. 
def send_nda_email(to, copy, subject, template, **kwargs):
	msg = Message(subject, sender=app.config['MAIL_SENDER'], recipients=to, cc=copy)
	msg.body = render_template(template + '.txt', **kwargs)
	msg.html = render_template(template + '.html', **kwargs)
	mail.send(msg)

@app.route('/nda_confirmation/<user_email>')
def nda_confirmation(user_email):
	user_email = user_email
	recipient_first_name = session.get('recipient first name')
	recipient_last_name = session.get('recipient last name')
	recipient_name = recipient_first_name + ' ' + recipient_last_name
	recipient_email = session.get('party email')
	
	send_nda_email([recipient_email], [user_email], 'TSports NDA for Signature', 'mail/nda_email', 
					recipient_name=recipient_name, user_email=user_email) 
	
	return redirect(url_for('nda_send_confirmation'))
	
@app.route('/nda_send_confirmation')
def nda_send_confirmation():
	user_email = session.get('email')
	recipient_first_name = session.get('recipient first name')
	recipient_last_name = session.get('recipient last name')
	recipient_name = recipient_first_name + ' ' + recipient_last_name
	recipient_email = session.get('party email')
	return render_template('nda_send_confirmation.html', 
							recipient_name=recipient_name, 
							recipient_email=recipient_email,
							user_email=user_email)

@app.route('/thanks_for_signing')
def thanks_for_signing():
	return render_template('thanks_for_signing.html', party_email = session.get('party email'))

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404
	
@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500
	
#Database tables
class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(64), unique=True, index=True)
	password = db.Column(db.String(64), index=True)
	
	def __repr__(self):
		return '<User %r>' % self.email
		
class NDA_Party(db.Model):
	__tablename__ = 'nda_parties'
	id = db.Column(db.Integer, primary_key=True)
	signatory_name = db.Column(db.String(200))
	signatory_title = db.Column(db.String(200))
	email = db.Column(db.String(120), unique=True)
	company_name = db.Column(db.String(200))
	company_address = db.Column(db.String(250))
	city = db.Column(db.String(100))
	state = db.Column(db.String(64))
	zip_code = db.Column(db.String(10)) 
	
	def __init__(self, signatory_name, signatory_title, email,
				company_name, company_address, city, state,
				zip_code):

		self.signatory_name = signatory_name
		self.signatory_title = signatory_title
		self.email = email
		self.company_name = company_name
		self.company_address = company_address
		self.city = city
		self.state = state
		self.zip_code = zip_code
	
	def __repr__(self):
		return '<User %r>' % self.signatory_name
	
#Adds shell context to manager
def make_shell_context():
	return dict(app=app, db=db, User=User)

manager.add_command("shell", Shell(make_context=make_shell_context))

#Adds database migration command to manager
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand) 
	
if __name__ == '__main__':
	manager.run()