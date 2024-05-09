"""Sign-up & log-in forms."""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList, FormField, BooleanField, Form
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional
)

class EntryForm(FlaskForm):
    search_target = StringField('Search')
    submit = SubmitField('Search')

