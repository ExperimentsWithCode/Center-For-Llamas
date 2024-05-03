from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for
# from flask_login import current_user, login_required

from flask import Response
from flask import request

from datetime import datetime
import json
import plotly
import plotly.express as px

from .models import format_df

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
    # local_df_curve_gauge_registry = df_curve_gauge_registry.sort_values("deployed_timestamp", axis = 0, ascending = False)
    # local_df_curve_gauge_registry
    df_approved = get_approved()
    df_deployed = get_deployed()

    df_approved_grouped = get_checkpoint_counts(df_approved, True)
    df_deployed_grouped = get_checkpoint_counts(df_deployed, False)
    

    fig = px.bar(df_approved_grouped,
                    x=df_approved_grouped['first_period_end_date'],
                    y=df_approved_grouped['gauge_addr'],
                    color='source',
                    title='Gauges Voted in Per Checkpoint',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    
                    )
    # fig.update_layout(yaxis_range=[0,15])
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.bar(df_deployed_grouped,
                    x=df_deployed_grouped['deployed_period_end_date'],
                    y=df_deployed_grouped['gauge_addr'],
                    color='source',
                    title='Gauges Deployed Per Checkpoint',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    
                    )
    # fig.update_layout(yaxis_range=[0,15])
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    df_approved_source_groups = df_approved.groupby(['source'])['gauge_addr'].count()
    df_approved_source_groups = df_approved_source_groups.to_frame().reset_index()
    df_approved_source_groups = df_approved_source_groups.sort_values(['gauge_addr'], ascending=False)

    fig = px.bar(df_approved_source_groups,
                    x=df_approved_source_groups['source'],
                    y=df_approved_source_groups['gauge_addr'],
                    color='source',
                    title='Gauges Approved by Source (only distinguishes tracked factories)',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    
                    )
    # fig.update_layout(yaxis_range=[0,15])
    # fig.show()
    graphJSON3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    df_deployed_source_groups = df_deployed.groupby(['source'])['gauge_addr'].count()
    df_deployed_source_groups = df_deployed_source_groups.to_frame().reset_index()
    df_deployed_source_groups = df_deployed_source_groups.sort_values(['gauge_addr'], ascending=False)

    fig = px.bar(df_deployed_source_groups,
                    x=df_deployed_source_groups['source'],
                    y=df_deployed_source_groups['gauge_addr'],
                    color='source',
                    title='Gauges Deployed by Source (only includes tracked factories)',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    
                    )
    # fig.update_layout(yaxis_range=[0,15])
    # fig.show()
    graphJSON4 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template(
        'gauge_index.jinja2',
        title='Curve Gauges',
        template='gauge-votes-show',
        body="",
        # df_curve_gauge_registry = local_df_curve_gauge_registry,
        df_approved = df_approved,
        df_deployed = df_deployed,
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
        graphJSON3 = graphJSON3,
        graphJSON4 = graphJSON4
    )


@gauges_bp.route('/show/<string:gauge_addr>', methods=['GET'])
# @login_required
def show(gauge_addr):
    df_curve_gauge_registry = app.config['df_curve_gauge_registry']
    local_df_curve_gauge_registry = df_curve_gauge_registry[df_curve_gauge_registry['gauge_addr'] == gauge_addr]
    return render_template(
        'gauge_show.jinja2',
        title='Curve Gauges',
        template='gauge-votes-show',
        body="",
        df_curve_gauge_registry = local_df_curve_gauge_registry
        # graphJSON = graphJSON
    )




def get_approved():
    df_curve_gauge_registry = app.config['df_curve_gauge_registry']
    return df_curve_gauge_registry.dropna(subset=['vote_timestamp']).sort_values(['vote_timestamp'], ascending=False)

def get_deployed():
    df_curve_gauge_registry = app.config['df_curve_gauge_registry']
    return df_curve_gauge_registry.dropna(subset=['deployed_timestamp']).sort_values(['deployed_timestamp'], ascending=False)

def get_checkpoint_counts(df, is_approved=False):
    if is_approved:
        df_grouped = df.groupby(['first_period_end_date', 'source'])['gauge_addr'].count()
        df_grouped = df_grouped.to_frame().reset_index()
        df_grouped = df_grouped.sort_values(['first_period_end_date', 'gauge_addr'], ascending=False)
    else:
        df_grouped = df.groupby(['deployed_period_end_date', 'source'])['gauge_addr'].count()
        df_grouped = df_grouped.to_frame().reset_index()
        df_grouped = df_grouped.sort_values(['deployed_period_end_date', 'gauge_addr'], ascending=False)
    return df_grouped