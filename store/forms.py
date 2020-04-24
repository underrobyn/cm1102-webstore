from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
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
	submit = SubmitField("Add")


class UpdatePasswordForm(FlaskForm):
	password = PasswordField('Current Password', validators=[DataRequired(), Length(min=password_req["min"], max=password_req["max"])])
	new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=password_req["min"], max=password_req["max"])])
	confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])


class DeleteAccountForm(FlaskForm):
	password = PasswordField('Account Password', validators=[DataRequired(), Length(min=password_req["min"], max=password_req["max"])])
	confirm_delete = BooleanField("Are you sure?", validators=[DataRequired()])