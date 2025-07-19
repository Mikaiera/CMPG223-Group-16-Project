from flask_wtf import FlaskForm
from wtforms import StringField 
from wtforms.validators import Length


class Search(FlaskForm):
    query = StringField('Title')