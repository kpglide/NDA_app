import os
from flask import Flask, request, render_template, session, redirect, url_for
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, SubmitField, BooleanField
from wtforms.validators import Required, Email, Length
from flask.ext.sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
#For production, change secret key and move it to an environment variable
app.config['SECRET_KEY'] = 'development_key'
app.config['SQLALCHEMY_DATABASE_URI'] = \
	'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
manager = Manager(app)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

#Forms
class LoginForm(Form):
	#For production, consider updating email field validation to only accept
	#addresses from a specified domain
	email = TextField('Email Address', validators=[Required(), Email()])
	password = PasswordField('Password', validators=[Required(), Length(min=6, max=15)])
	submit = SubmitField('Log In')
	remember_me = BooleanField('Keep me logged in')

@app.route('/', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		session['email'] = form.email.data
		return redirect(url_for('login'))		
	return render_template('login.html', form=form, email=session.get('email'))
	#return jsonify({'ip': request.remote_addr}), 200

#Routes	
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
	
if __name__ == '__main__':
	manager.run()