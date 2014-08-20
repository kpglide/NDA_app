from flask import render_template, session, request, redirect, url_for, flash
from . import main
import os
from .forms import LoginForm, RecipientForm, SignatoryForm
from .. import db
from ..models import User, NDA_Party
from ..email import send_nda_email

#Routes
@main.route('/', methods=['GET', 'POST'])
def login():
	#TODO:  Fix other views so that they're not accessible unless user is logged in
	#TODO:  Add logout link
	form = LoginForm()
	if form.validate_on_submit():
		if form.password.data == 'testtest':
			session['email'] = form.email.data
			return redirect(url_for('.home'))
		else:
			return redirect(url_for('.login'))		
	return render_template('login.html', form=form, email=session.get('email'))

@main.route('/home')
def home():
	return render_template('home.html')
	
@main.route('/create_nda', methods=['GET', 'POST'])
def create_nda():
	form = RecipientForm()
	if form.validate_on_submit():
		session['recipient first name'] = form.firstname.data
		session['recipient last name'] = form.lastname.data
		session['party email'] = form.email.data
		return redirect(url_for('.nda_preview'))
	else:
		return render_template('create_nda.html', form=form)

@main.route('/nda_preview')
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

@main.route('/nda/<user_email>', methods=['GET', 'POST'])
def nda(user_email):
	error = None
	f = open('app/static/Very Short NDA.txt', 'r')
	data = f.read().decode('utf-8') 
	paragraphs = data.split("\n\n")
	f.close()
	form = SignatoryForm()
	user_email = user_email
	if form.validate_on_submit() and (request.form.get("accept") == "y"):		
		party = NDA_Party(form.signatory_name.data, form.signatory_title.data,
							form.email.data, form.company_name.data, form.company_address.data,
							form.city.data, form.state.data, form.zip_code.data)
		#TODO: Use Flask-Moment to record click-through date
		#here as the NDA signature date
		db.session.add(party)
		session['party email'] = party.email
		send_nda_email([party.email], [user_email], 
						'Signed NDA for ' + party.signatory_name + '//' +
						party.company_name, 
						'mail/signed_nda', signatory_name=party.signatory_name, 
						user_email=user_email, company_name=party.company_name, 
						signatory_title=party.signatory_title, paragraphs=paragraphs,
						) 
		return redirect(url_for('.thanks_for_signing'))
	if request.method == 'POST' and request.form.get("accept") != "y":
		error = "You must check the box indicating you accept the terms of the NDA."
	return render_template('nda.html', user_email=user_email, paragraphs=paragraphs,
							form=form, error=error)
								
@main.route('/nda_confirmation/<user_email>')
def nda_confirmation(user_email):
	user_email = user_email
	recipient_first_name = session.get('recipient first name')
	recipient_last_name = session.get('recipient last name')
	recipient_name = recipient_first_name + ' ' + recipient_last_name
	recipient_email = session.get('party email')
	
	send_nda_email([recipient_email], [user_email], 'TSports NDA for Signature', 'mail/nda_email', 
					recipient_name=recipient_name, user_email=user_email) 
	
	return redirect(url_for('.nda_send_confirmation'))
	
@main.route('/nda_send_confirmation')
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

@main.route('/thanks_for_signing')
def thanks_for_signing():
	return render_template('thanks_for_signing.html', party_email = session.get('party email'))
