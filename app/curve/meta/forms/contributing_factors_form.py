"""Sign-up & log-in forms."""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
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


