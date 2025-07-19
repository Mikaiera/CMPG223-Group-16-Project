from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, IntegerField, DateField, PasswordField,SelectField
from wtforms.validators import DataRequired, Length, Email

from pycountry import countries

country_names = [c.name for c in countries]
country_names.sort()

class AddComic(FlaskForm):
    cover_image = FileField('Book cover', validators=[FileAllowed(['jpg', 'png']), DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    illustrator = StringField('Illustrator', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()], default=0)
    date = DateField('Date', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=300)])
    stock_quantity = IntegerField('Stock Quantity', validators=[DataRequired()])
    top_pick = BooleanField('Best seller')
    submit = SubmitField('Add Book')


class AddFreelancer(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    country = SelectField('Country', validators=[DataRequired()], choices=country_names, default=country_names[0])
    submit = SubmitField('Add Freelancer')

class AddCustomer(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    country = SelectField('Country', validators=[DataRequired()], choices=country_names, default=country_names[0])
    submit = SubmitField('Add Customer')