from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for
# from flask_login import current_user, login_required

from flask import Response
from flask import request

from datetime import datetime
import json
import plotly
import plotly.express as px

from .models import df_curve_gauge_registry

# Blueprint Configuration
gauges_bp = Blueprint(
    'gauges_bp', __name__,
    url_prefix='/curve/gauges',
    template_folder='templates',
    static_folder='static'
)


@gauges_bp.route('/', methods=['GET'])
# @login_required
def index():
    return redirect(url_for('gauge_rounds.index'))