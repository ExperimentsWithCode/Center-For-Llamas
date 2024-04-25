"""Sign-up & log-in forms."""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextAreaField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional
)


class ContributingFactorsForm(FlaskForm):
    """User Sign-up Form."""
    target_gauge = StringField(
        'Target Gauge',
        validators=[DataRequired()]
    )
    compare_back = IntegerField(
        'Compare Back',
        # validators=[DataRequired()]
    )
    # top_results = IntegerField(
    #     'Top Results',
    #     validators=[DataRequired()]
    # )
    submit = SubmitField('Submit')


class ContributingFactorsCompareForm(FlaskForm):
    """User Sign-up Form."""
    target_gauges = TextAreaField(
        'Target Gauges', 
        # [validators.optional(), validators.length(max=1100)]
        )
    compare_back = IntegerField(
        'Compare Back',
        # validators=[DataRequired()]
    )
    # top_results = IntegerField(
    #     'Top Results',
    #     validators=[DataRequired()]
    # )
    submit = SubmitField('Submit')


