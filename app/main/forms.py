from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, SubmitField, BooleanField,\
	SelectField
from wtforms.validators import Required, Email, Length, Regexp, InputRequired
from ..models import User, NDA_Party


#List of tuples containing abbreviation / full-name pairs for the US states
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
	
class SignatoryForm(Form):
	state_choices = us_states()
	#TODO--NEED TO FIX CSS HERE SO THAT AN ERROR MESSAGE APPEARS WHEN
	#THIS BOX IS NOT CHECKED
	accept = BooleanField('''I am an authorized signatory of the company indicated below.  
							I agree to the terms of the Non-Disclosure Agreement above on 
							behalf of my company.''',
							validators=[InputRequired("Please check")])
	company_name = TextField('Company Name (Full Legal Entity Name)', validators=[Required()])
	signatory_name = TextField('Your Name', validators=[Required()])
	signatory_title = TextField('Your Title', validators=[Required()])
	email = TextField('Email Address', validators=[Required(), Email()])
	company_address = TextField('Company Street Address', validators=[Required()])
	city = TextField('City', validators=[Required()])
	state = SelectField('State', choices=state_choices, validators=[Required()])
	zip_code = TextField('Zip or Postal Code', validators=[Required(), Regexp(u'^(\d{5}(-\d{4})?)$')])
	submit = SubmitField('I Agree')