from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, EmailField, PasswordField
from wtforms.validators import InputRequired, NumberRange, email_validator

class RegisterUserForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    email = EmailField('Email address', validators=[InputRequired()])
    pw = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Register')

class LoginUserForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired()])
    pw = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

class NewStoreForm(FlaskForm):
    name = StringField('Cafe name', validators=[InputRequired()])
    maps_url = StringField('Maps URL (optional)', validators=[InputRequired()])
    seating = IntegerField('How many seats are available?', validators=[InputRequired()])
    wifi_rating = IntegerField('How was the wifi? (On a scale of 1-5)', validators=[NumberRange(min=1, max=5)])
    power_rating = IntegerField('How was the power outlet availability? (On a scale of 1-5)', validators=[NumberRange(min=1, max=5)])
    submit = SubmitField(label='Submit')