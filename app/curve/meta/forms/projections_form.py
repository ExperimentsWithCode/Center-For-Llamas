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


class PowerDiffForm(FlaskForm):
    """User Sign-up Form."""
    main_round = IntegerField(
        'Main Round',
        # validators=[DataRequired()]
    )
    compare_round = IntegerField(
        'Compare Round',
        validators=[DataRequired()]
    )
    top_results = IntegerField(
        'Top Results',
        validators=[DataRequired()]
    )
    submit = SubmitField('Submit')


