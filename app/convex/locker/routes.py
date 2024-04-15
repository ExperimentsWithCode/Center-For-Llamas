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


# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# from matplotlib.figure import Figure
# import io

from app.convex.locker.models import df_locker

from app.utilities.utility import (
    format_plotly_figure,
    get_now,
    get_address_profile
)

# Blueprint Configuration
convex_vote_locker_bp = Blueprint(
    'convex_vote_locker_bp', __name__,
    url_prefix='/convex/vote_locker',
    template_folder='templates',
    static_folder='static'
)

# df_vote_aggregates = app.config['df_convex_snapshot_vote_aggregates']
# df_vote_choice = app.config['df_convex_snapshot_vote_choice']


# proposal_end	proposal_title	choice	sum	count

@convex_vote_locker_bp.route('/', methods=['GET'])
# @login_required
def index():

    df_locker_agg_system = app.config['df_convex_locker_agg_system']
    df_locker_agg_current = app.config['df_convex_locker_agg_current']
    df_locker_agg_epoch = app.config['df_convex_locker_agg_epoch']
    # df_locker = app.config['df_convex_locker']
    df_locker_agg_user_epoch = app.config['df_convex_locker_agg_user_epoch']


    
    # Filter Data
    df_locker_agg_user_epoch_current = df_locker_agg_user_epoch[df_locker_agg_user_epoch['this_epoch'] >= get_now()]
    df_locker_agg_user_epoch_current = df_locker_agg_user_epoch_current[
        df_locker_agg_user_epoch_current['this_epoch'] == df_locker_agg_user_epoch_current.this_epoch.min()
        ]
    df_locker_agg_user_epoch_current = df_locker_agg_user_epoch_current.sort_values('current_locked', axis=0, ascending=False)
    
    
    local_df_locker_agg_user_epoch = df_locker_agg_user_epoch.groupby([
            'this_epoch',
            'known_as',
        ]).agg(
        current_locked=pd.NamedAgg(column='current_locked', aggfunc=sum)
        ).reset_index()
    
    local_df_locker_agg_user_epoch = local_df_locker_agg_user_epoch.sort_values(['this_epoch', 'current_locked'], axis = 0, ascending = False)
    # df_locker_agg_user_epoch_current =  df_locker_agg_user_epoch[df_locker_agg_user_epoch['end_date']]
    # local_df_gauge_votes = df_all_by_gauge.groupby(['voter', 'gauge_addr'], as_index=False).last()

    # Build chart
    fig = make_subplots()
    fig.update_layout(
        title=f"Convex: vlCVX Current Locked Per Epoch",
        #     xaxis_title="X Axis Title",
        #     yaxis_title="Y Axis Title",
        #     legend_title="Legend Title",
        # height= 1000,
    )
    fig = fig.add_trace(
        go.Bar(
            x=df_locker_agg_current.epoch_start.dt.date,
            y=df_locker_agg_current.locked_amount,
            name="Locked",
            # color="pool_name"
        ),
        secondary_y=False
    )
    fig = fig.add_trace(
        go.Bar(
            x = df_locker_agg_current.epoch_end.dt.date,
            y = df_locker_agg_current.locked_amount, 
            name = "Lock Expires",
            # line_shape='hvh',
            # line_width=3,
        ),
        # secondary_y=True
    )
    fig.add_vline(x=get_now(), line_width=2, line_dash="dash", line_color="black" )

    fig.update_layout(autotypenumbers='convert types')
    fig = format_plotly_figure(fig)

    # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)



    fig = make_subplots()
    fig.update_layout(
        title=f"Convex: vlCVX Locked Per Epoch",
        #     xaxis_title="X Axis Title",
        #     yaxis_title="Y Axis Title",
        #     legend_title="Legend Title",

        # height= 1000,
    )
    fig = fig.add_trace(
        go.Bar(
            x=df_locker_agg_epoch.epoch_start.dt.date,
            y=df_locker_agg_epoch.locked_amount,
            name="Locked",
            # color="pool_name"
        ),
        secondary_y=False
    )
    fig = fig.add_trace(
        go.Bar(
            x=df_locker_agg_epoch.epoch_end.dt.date,
            y=df_locker_agg_epoch.locked_amount,
            name="Lock Expires",
            # color="pool_name"
        ),
        secondary_y=False
    )
    fig.add_vline(x=get_now(), line_width=2, line_dash="dash", line_color="black")
    fig = format_plotly_figure(fig)

    # # Build Plotly object
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_layout(
        title=f"Convex Locker Historic Total Locked",
            xaxis_title="Epoch Date",
            yaxis_title="vlCVX",
            yaxis2_title="Locked Positions",
        #     legend_title="Legend Title",
        # height= 1000,
    )

    fig = fig.add_trace(
        go.Scatter(
            x = df_locker_agg_system.this_epoch,
            y = df_locker_agg_system.lock_count, 
            name = "Lock Count",
            line_shape='hvh',
            line_width=3,
        ),
        secondary_y=True
    )

    fig = fig.add_trace(
        go.Scatter(
            x = df_locker_agg_system.this_epoch,
            y = df_locker_agg_system.user_count, 
            name = "User Count",
            line_shape='hvh',
            line_width=3,
        ),
        secondary_y=True
    )
    fig = fig.add_trace(
        go.Bar(
            x=df_locker_agg_system.this_epoch,
            y=df_locker_agg_system.total_locked,
            name="Total Locked",
            # color="pool_name"
        ),
        secondary_y=False
    )

    fig.add_vline(x=get_now(), line_width=3, line_dash="dash", line_color="black", )

    fig.update_layout(autotypenumbers='convert types')
    fig.update_yaxes(rangemode="tozero")
    fig = format_plotly_figure(fig)

    # # Build Plotly object
    graphJSON3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    fig = px.line(local_df_locker_agg_user_epoch,
                    x=local_df_locker_agg_user_epoch['this_epoch'].dt.date,
                    y=local_df_locker_agg_user_epoch['current_locked'],
                    color='known_as',
                    line_shape='linear',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    fig.add_vline(x=get_now(), line_width=2, line_dash="dash", line_color="black")
    fig.update_layout(
        title=f"Convex vlCVX Balances",
            xaxis_title="This Epoch",
            yaxis_title="vlCVX Balance",
        #     legend_title="Legend Title",
        # height= 1000,
    )
    fig = format_plotly_figure(fig)

    graphJSON4 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template(
        'index_convex_vote_locker.jinja2',
        title='Convex Vote Locker',
        template='convex-vote-locker-index',
        body="",
        # sum_current_votes = df_current_votes.total_vote_power.sum(),
        # sum_prior_votes = df_prior_votes.total_vote_power.sum(),
        # convex_agg_vote_locks = df_locker_agg_system,
        # convex_agg_epoch_vote_locks_current = df_locker_agg_current,
        convex_locker = df_locker_agg_user_epoch_current,
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
        graphJSON3 = graphJSON3,
        graphJSON4 = graphJSON4,

    )



@convex_vote_locker_bp.route('/voter/<string:user>', methods=['GET'])
# @login_required
def show(user):
    df_locker_user_epoch = app.config['df_convex_locker_user_epoch']
    df_locker_agg_user_epoch = app.config['df_convex_locker_agg_user_epoch']
    df_locker = app.config['df_convex_locker']

    
    # Filter Data
    local_df_locker_agg_user_epoch = df_locker_agg_user_epoch[df_locker_agg_user_epoch['user'] == user]
    local_df_locker = df_locker[df_locker['user'] == user]

    local_df_locker_current = local_df_locker[local_df_locker['epoch_end'] >=  get_now()]

    # local_df_gauge_votes = df_all_by_gauge.groupby(['voter', 'gauge_addr'], as_index=False).last()

    # Build chart
    fig = make_subplots()
    fig.update_layout(
        title=f"Convex: vlCVX Current Locked Per Epoch",
        #     xaxis_title="X Axis Title",
        #     yaxis_title="Y Axis Title",
        #     legend_title="Legend Title",
        # height= 1000,
    )
    fig = fig.add_trace(
        go.Bar(
            x=local_df_locker_current.epoch_start.dt.date,
            y=local_df_locker_current.locked_amount,
            name="Locked",
            # color="pool_name"
        ),
        secondary_y=False
    )
    fig = fig.add_trace(
        go.Bar(
            x = local_df_locker_current.epoch_end.dt.date,
            y = local_df_locker_current.locked_amount, 
            name = "Lock Expires",
            # line_shape='hvh',
            # line_width=3,
        ),
        # secondary_y=True
    )
    fig.add_vline(x=get_now(), line_width=2, line_dash="dash", line_color="black" )

    fig.update_layout(autotypenumbers='convert types')
    # fig.update_yaxes(rangemode="tozero")
    fig = format_plotly_figure(fig)

    # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    fig = make_subplots()
    fig.update_layout(
        title=f"Convex: vlCVX Locks Per Epoch",
        #     xaxis_title="X Axis Title",
        #     yaxis_title="Y Axis Title",
        #     legend_title="Legend Title",
        # height= 1000,
    )
    fig = fig.add_trace(
        go.Bar(
            x=local_df_locker.epoch_start.dt.date,
            y=local_df_locker.locked_amount,
            name="Locked",
            # color="pool_name"
        ),
        secondary_y=False
    )
    fig = fig.add_trace(
        go.Bar(
            x = local_df_locker.epoch_end.dt.date,
            y = local_df_locker.locked_amount, 
            name = "Lock Expires",
            # line_shape='hvh',
            # line_width=3,
        ),
        # secondary_y=True
    )
    fig.add_vline(x=get_now(), line_width=2, line_dash="dash", line_color="black" )

    fig.update_layout(autotypenumbers='convert types')
    fig = format_plotly_figure(fig)

    # # Build Plotly object
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_layout(
        title=f"Convex Locker Historic Total Locked",
            xaxis_title="Epoch Date",
            yaxis_title="vlCVX",
            yaxis2_title="Locked Positions",
        #     legend_title="Legend Title",
        # height= 1000,
    )
    fig = fig.add_trace(
        go.Bar(
            x=local_df_locker_agg_user_epoch.this_epoch,
            y=local_df_locker_agg_user_epoch.current_locked,
            name="Total Locked",
            # color="pool_name"
        ),
        secondary_y=False
    )
    fig = fig.add_trace(
        go.Scatter(
            x = local_df_locker_agg_user_epoch.this_epoch,
            y = local_df_locker_agg_user_epoch.lock_count, 
            name = "Locked Count",
            line_shape='hvh',
            line_width=3,
        ),
        secondary_y=True
    )
    fig.add_vline(x=get_now(), line_width=3, line_dash="dash", line_color="black", )

    fig.update_layout(autotypenumbers='convert types')
    fig.update_yaxes(rangemode="tozero")
    fig = format_plotly_figure(fig)

    # # Build Plotly object
    graphJSON3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        'show_convex_vote_locker.jinja2',
        title='Convex Vote Locker User',
        template='convex-vote-locker-index',
        body="",
        actor_profile = get_address_profile(app.config['df_actors'], user),

        # sum_current_votes = df_current_votes.total_vote_power.sum(),
        # sum_prior_votes = df_prior_votes.total_vote_power.sum(),
        # convex_agg_vote_locks = df_locker_agg_system,
        # convex_agg_epoch_vote_locks_current = df_locker_agg_current,
        convex_locker = local_df_locker,
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
        graphJSON3 = graphJSON3
    )