from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, BooleanField, DecimalField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp, NumberRange
from store.config import password_req
import re


class CreateUserForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired(), Length(min=1, max=50)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired(), Length(min=password_req["min"], max=password_req["max"])])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Create Account')


class LoginUserForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired(), Length(min=password_req["min"], max=password_req["max"])])
	submit = SubmitField('Login')


def postcode_validate(form, field):
	postcode_re = re.compile(r'\b[A-Z]{1,2}[0-9][A-Z0-9]? [0-9][ABD-HJLNP-UW-Z]{2}\b')
	if postcode_re.match(field.data):
		return True
	return False


class AddAddressForm(FlaskForm):
	postcode = StringField('PostCode', validators=[DataRequired(), postcode_validate])
	houseid = StringField('(House / Building / Flat) Number', validators=[DataRequired()])
	street = StringField('Street', validators=[DataRequired()])
	city = StringField('City / Town', validators=[DataRequired()])
	submit = SubmitField('Add Address')


class UpdateEmailForm(FlaskForm):
	email = StringField('New Email', validators=[DataRequired(), Email()])
	password = PasswordField('Current Password', validators=[DataRequired()])
	submit = SubmitField('Update Email')


class AddToCart(FlaskForm):
	quantity = IntegerField('Quantity: ', validators=[DataRequired()])
	submit = SubmitField('Add')


class UpdatePasswordForm(FlaskForm):
	password = PasswordField('Current Password', validators=[DataRequired(), Length(min=password_req["min"], max=password_req["max"])])
	new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=password_req["min"], max=password_req["max"])])
	confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
	submit = SubmitField('Update Password')


class DeleteFromCart(FlaskForm):
	delete = SubmitField('Clear Cart')


class DeleteAccountForm(FlaskForm):
	password = PasswordField('Account Password', validators=[DataRequired(), Length(min=password_req["min"], max=password_req["max"])])
	confirm_delete = BooleanField('Are you sure?', validators=[DataRequired()])
	submit = SubmitField('Delete Account')


class DownloadDataForm(FlaskForm):
	password = PasswordField('Account Password', validators=[DataRequired(), Length(min=password_req["min"], max=password_req["max"])])
	submit = SubmitField('Download Data')


class InputBillingForm(FlaskForm):
	card_number = StringField('Card Number (e.g. "1234567891012345")', validators=[DataRequired()])
	card_cvc = StringField('Card CVC (e.g. "123")', validators=[DataRequired()])
	card_end = StringField('Card End (e.g. "12/24")', validators=[DataRequired()])
	submit = SubmitField('Place Order')


class ProductReviewForm(FlaskForm):
	rating = DecimalField('Rating (0 - 5 stars)', validators=[NumberRange(min=0, max=5, message='Review between 0 and 5 stars')])
	review = TextAreaField('Your review', validators=[Length(min=0, max=2000)])
	submit = SubmitField('Leave Review')