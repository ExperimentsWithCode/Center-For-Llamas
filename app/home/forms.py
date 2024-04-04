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

class EntryForm(Form):
    component_name = StringField('Component Name')
    run_component = BooleanField('Run Component')


class DataManagerForm(FlaskForm):
    """Filters what to load and process"""
    load_initial = BooleanField(
    'Load Initial',
    # validators=[DataRequired()]
    )
    should_fetch = BooleanField(
    'Should Fetch',
    # validators=[DataRequired()]
    )
    load_cutoff = BooleanField(
    'Load Cutoff ',
    # validators=[DataRequired()]
    )
    manager_config = FieldList(FormField(EntryForm))

    submit = SubmitField('Submit')



    # not subclassing from flask_wtf.FlaskForm
# in order to avoid CSRF on subforms


