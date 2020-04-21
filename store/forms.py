from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp


class CreateUserForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired(), Length(min=1,max=50)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=256)])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Create Account')


class LoginUserForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=256)])
	submit = SubmitField('Login')


class UpdateEmailForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Current Password', validators=[DataRequired()])
	submit = SubmitField('Update Email')


class UpdatePasswordForm(FlaskForm):
	current_password = PasswordField('Current Password', validators=[DataRequired(), Length(min=6, max=256)])
	new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6, max=256)])
	confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])