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


# @gauges_bp.route('/', methods=['GET'])
# # @login_required
# def index():
#     return render_template(
#         'gauge_index.jinja2',
#         title='Curve Gauge Votes',
#         template='gauge-votes-show',
#         body="",
#         df_curve_gauge_registry = df_curve_gauge_registry
#         # graphJSON = graphJSON
#     )


@gauges_bp.route('/', methods=['GET'])
# @login_required
def index():
    local_df_curve_gauge_registry = df_curve_gauge_registry.sort_values("deployed_timestamp", axis = 0, ascending = False)
    local_df_curve_gauge_registry


    df2 = df_curve_gauge_registry.groupby(['first_period_end_date', 'source'])['gauge_addr'].count()
    df2 = df2.to_frame().reset_index()

    fig = px.bar(df2,
                    x=df2['first_period_end_date'],
                    y=df2['gauge_addr'],
                    color='source',
                    title='Gauges Voted in Per Round',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    
                    )
    fig.update_layout(yaxis_range=[0,15])
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template(
        'gauge_index.jinja2',
        title='Curve Gauges',
        template='gauge-votes-show',
        body="",
        df_curve_gauge_registry = local_df_curve_gauge_registry,
        graphJSON = graphJSON,
    )


@gauges_bp.route('/show/<string:gauge_addr>', methods=['GET'])
# @login_required
def show(gauge_addr):
    local_df_curve_gauge_registry = df_curve_gauge_registry[df_curve_gauge_registry['gauge_addr'] == gauge_addr]
    return render_template(
        'gauge_show.jinja2',
        title='Curve Gauges',
        template='gauge-votes-show',
        body="",
        df_curve_gauge_registry = local_df_curve_gauge_registry
        # graphJSON = graphJSON
    )