from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from .. models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1,64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1,64), Regexp('^[A-za-z][A-Za-z0-9_.]*$', 0 ,'Username must contain only letters, numners . or _')])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field): # 'validate_'filedName prefix defines a customvalidator.  It is invoked in addition to the standard validators
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already in use.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')