from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for
# from flask_login import current_user, login_required

from flask import Response
from flask import request

from datetime import datetime as dt
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app.data.local_storage import pd
from app.utilities.utility import get_address_profile

# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# from matplotlib.figure import Figure
# import io

from app.stakedao.staked_sdcrv.models import df_stakedao_sdcrv, df_stakedao_sdcrv_known, df_stakedao_sdcrv_agg



# Blueprint Configuration
stakedao_staked_sdcrv_bp = Blueprint(
    'stakedao_staked_sdcrv_bp', __name__,
    url_prefix='/stakedao/staked_sdcrv',
    template_folder='templates',
    static_folder='static'
)




@stakedao_staked_sdcrv_bp.route('/', methods=['GET'])
# @login_required
def index():
    df_stakedao_sdcrv = app.config['df_stakedao_sdcrv']
    df_stakedao_sdcrv_known = app.config['df_stakedao_sdcrv_known']
    df_stakedao_sdcrv_agg = app.config['df_stakedao_sdcrv_agg']

    # Filter Data
    local_df_stakedao_sdcrv = df_stakedao_sdcrv.sort_values('date').groupby(['provider']).tail(1)
    local_df_stakedao_sdcrv = local_df_stakedao_sdcrv.sort_values('date').groupby(['provider']).head(1)
    local_df_stakedao_sdcrv = local_df_stakedao_sdcrv.sort_values('staked_balance',  axis = 0, ascending = False)
    # Build chart
    fig = px.area(df_stakedao_sdcrv_agg,
                    x=df_stakedao_sdcrv_agg['date'],
                    y=df_stakedao_sdcrv_agg['total_staked_balance'],
                    # color='known_as',
                    # line_shape='linear',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    # fig.add_vline(x=dt.utcnow(), line_width=2, line_dash="dash", line_color="black")
    fig.update_layout(
        title=f"StakeDAO sdCRV Total Staked",
            xaxis_title="Date",
            yaxis_title="Staked sdCRV",
        #     legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        ),
        # height= 1000,
    )

    # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)



    fig = px.line(df_stakedao_sdcrv_agg,
                    x=df_stakedao_sdcrv_agg['date'],
                    y=df_stakedao_sdcrv_agg['balance_delta'],
                    # color='known_as',
                    # line_shape='linear',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    # fig.add_vline(x=dt.utcnow(), line_width=2, line_dash="dash", line_color="black")
    fig.update_layout(
        title=f"Staked sdCRV Total Balance Changes",
            xaxis_title="Date",
            yaxis_title="Staked sdCRV Balance Delta",
        #     legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        ),
        # height= 1000,
    )

    # # Build Plotly object
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    
    fig = px.line(df_stakedao_sdcrv_known,
                    x=df_stakedao_sdcrv_known['date'],
                    y=df_stakedao_sdcrv_known['staked_balance'],
                    color='known_as',
                    line_shape='hv',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    # fig.add_vline(x=dt.utcnow(), line_width=2, line_dash="dash", line_color="black")
    fig.update_layout(
        title=f"StakeDAO Staked sdCRV Balances",
            xaxis_title="Date",
            yaxis_title="Staked sdCRV Balance",
        #     legend_title="Legend Title",
        font=dict(        family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        ),
        # height= 1000,
    )

    # # Build Plotly object
    graphJSON3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)



    return render_template(
        'index_stakedao_staked_sdcrv.jinja2',
        title='StakeDAO Staked sdCRV',
        template='stakedao-staked-sdcrv-index',
        body="",
        # sum_current_votes = df_current_votes.total_vote_power.sum(),
        # sum_prior_votes = df_prior_votes.total_vote_power.sum(),
        # convex_agg_vote_locks = df_locker_agg_system,
        # convex_agg_epoch_vote_locks_current = df_locker_agg_current,
        stakedao_sd_crv = local_df_stakedao_sdcrv,
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
        graphJSON3 = graphJSON3

    )



@stakedao_staked_sdcrv_bp.route('/staker/<string:user>', methods=['GET'])
# @login_required
def show(user):
    df_stakedao_sdcrv = app.config['df_stakedao_sdcrv']
    # df_stakedao_sdcrv_known = app.config['df_stakedao_sdcrv_known']
    # df_stakedao_sdcrv_agg = app.config['df_stakedao_sdcrv_agg']

    
    # Filter Data
    local_df_stakedao_sdcrv = df_stakedao_sdcrv[df_stakedao_sdcrv['provider'] == user]
    # local_df_locker = df_locker[df_locker['user'] == user]

    # local_df_locker_current = local_df_locker[local_df_locker['epoch_end'] >= dt.utcnow()]

    # local_df_gauge_votes = df_all_by_gauge.groupby(['voter', 'gauge_addr'], as_index=False).last()

    # Build chart
    fig = px.area(local_df_stakedao_sdcrv,
                    x=local_df_stakedao_sdcrv['date'],
                    y=local_df_stakedao_sdcrv['staked_balance'],
                    # color='known_as',
                    line_shape='hv',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    
    fig.update_layout(
        title=f"Staked sdCRV Balance",
            xaxis_title="Date",
            yaxis_title="Staked sdCRV",
        #     legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        ),
        # height= 1000,
    )

    # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)



    fig = px.bar(local_df_stakedao_sdcrv,
                    x=local_df_stakedao_sdcrv['date'],
                    y=local_df_stakedao_sdcrv['balance_delta'],
                    color='event_name',
                    # line_shape='linear',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    # fig.add_vline(x=dt.utcnow(), line_width=2, line_dash="dash", line_color="black")
    fig.update_layout(
        title=f"Staked sdCRV Balance",
            xaxis_title="Date",
            yaxis_title="Staked sdCRV Balance Delta",
        #     legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        ),
        # height= 1000,
    )

    # # Build Plotly object
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # graphJSON3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        'show_stakedao_staked_sdcrv.jinja2',
        title='StakeDAO Staked sdCRV',
        template='stakedao-staked-sdcrv-show',
        body="",
        actor_profile = get_address_profile(app.config['df_actors'], user),

        # sum_current_votes = df_current_votes.total_vote_power.sum(),
        # sum_prior_votes = df_prior_votes.total_vote_power.sum(),
        # convex_agg_vote_locks = df_locker_agg_system,
        # convex_agg_epoch_vote_locks_current = df_locker_agg_current,
        stakedao_sd_crv = local_df_stakedao_sdcrv,
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2
    )