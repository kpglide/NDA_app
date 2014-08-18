from flask import current_app, request, url_for
from . import db

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