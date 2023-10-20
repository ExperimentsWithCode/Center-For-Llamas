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
    gauge_addr = StringField('Gauge Address:')
    delete = BooleanField('delete?')


class FilterLiquidityForm(FlaskForm):
    """Filters liquidity view to compare gauges with like features"""
    filter_asset = StringField(
        'Filter Asset',
        # validators=[DataRequired()]
    )
    head = IntegerField(
        'Head',
        # validators=[DataRequired()]
    )
    tail = IntegerField(
        'Tail',
        # validators=[DataRequired()]
    )
    source = StringField(
        'Source',
        # validators=[DataRequired()]
    )
    days_back = IntegerField(
        'Days Offset Back',
        # validators=[DataRequired()]
    )
    gauge_address_list = FieldList(FormField(EntryForm))

    submit = SubmitField('Submit')



    # not subclassing from flask_wtf.FlaskForm
# in order to avoid CSRF on subforms


