from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, EmailField, PasswordField, SubmitField, BooleanField, ValidationError,SelectField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange, Length

from website import bcrypt
from website.models import User
from pycountry import countries

country_names = [c.name for c in countries]
country_names.sort()


class SignUp(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=13, max=99)], default=13)
    phone = StringField('Phone', validators=[DataRequired()])
    country = SelectField('Country', validators=[DataRequired()], choices=country_names, default=country_names[0])
    address = StringField('Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(),
                    EqualTo('password', 'Passwords are not equal.')])
    remember = BooleanField('Remember me')
    submit = SubmitField('Sign up')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('This email is already in use! Please choose another one.')


class Login(FlaskForm):
    email = EmailField('Email', validators=[DataRequired('Please provide an email.'), Email()])
    password = PasswordField('Password', validators=[DataRequired('Please put in your password')])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')


class UpdateEmail(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Email')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('This email is already in use! Please use another one.')


class UpdatePassword(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Update Password')

    # def validate_current_password(self, current_password):
    #     password = User.query.filter_by(email=current_user.email,
    #                                     password=bcrypt.generate_password_hash(current_password.data)).first()
    #     if not password:
    #         raise ValidationError('Current password is incorrect!')

    def validate_new_password(self, new_password):
        if self.current_password.data == new_password.data:
            raise ValidationError('New password cannot be the same as the old password!')

# class deleteProfile(FlaskForm):
    