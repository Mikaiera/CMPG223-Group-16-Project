from flask_wtf import FlaskForm
from wtforms import EmailField, SubmitField, PasswordField, StringField
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange, ValidationError


class AddCardDetails(FlaskForm):
    first_name = StringField('First name', validators=[DataRequired('Please provide your first name.'),
                                                       Length(min=2, max=50)])
    last_name = StringField('Last name', validators=[DataRequired('Please provide your last name.'),
                                                     Length(min=2, max=50)])
    card_number = StringField('Card Number', validators=[DataRequired(), Length(min=19, max=19)])
    card_brand = SelectField('Select brand', validators=[DataRequired()],
                                choices=['Mastercard', 'Visa', 'Maestro'])
    cvv = StringField('CVV Number', validators=[DataRequired(), Length(min=3, max=3)])
    expiry_month = IntegerField('Month', validators=[DataRequired(), NumberRange(min=1, max=12)])
    expiry_year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=24, max=99)])
    submit = SubmitField('Add card')

    def validate_card_number(self, card_number):
        for i in card_number.data.replace(' ', ''):
            try:
                int(i)
            except:
                raise ValidationError('Invalid Card Number.')

    def validate_cvv(self, cvv):
        for i in cvv.data:
            try:
                int(i)
            except:
                raise ValidationError('Invalid CVV Number.')


class CheckOut(FlaskForm):
    submit = SubmitField('Confirm your order')


class RequestReset(FlaskForm):
    email = EmailField('Enter your email', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ResetPassword(FlaskForm):
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Update Password')
