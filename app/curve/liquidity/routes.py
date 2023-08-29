from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for
# from flask_login import current_user, login_required

from flask import Response
from flask import request

from datetime import datetime
import json
import plotly
import plotly.express as px

from .models import df_liquidity, df_processed_liquidity

# Blueprint Configuration
liquidity_bp = Blueprint(
    'curve_liquidity_bp', __name__,
    url_prefix='/curve/liquidity',
    template_folder='templates',
    static_folder='static'
)


@liquidity_bp.route('/', methods=['GET'])
# @login_required
def index():
    now = datetime.now()

    # Filter Data

    # local_df_gauge_votes = df_all_by_gauge.groupby(['voter', 'gauge_addr'], as_index=False).last()



    return render_template(
        'index_liqudity.jinja2',
        title='Curve Gauge Rounds',
        template='liquidity-index',
        body="",
        df_processed_liquidity = df_processed_liquidity,

    )

