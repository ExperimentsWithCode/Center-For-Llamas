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

from app.stakedao.locker.models import df_stakedao_vesdt, df_stakedao_vesdt_known, df_stakedao_vesdt_agg


from app.utilities.utility import (
    format_plotly_figure,
    get_lock_diffs,
)
# Blueprint Configuration
stakedao_locked_vesdt_bp = Blueprint(
    'stakedao_locked_vesdt_bp', __name__,
    url_prefix='/stakedao/staked_veSDT',
    template_folder='templates',
    static_folder='static'
)




@stakedao_locked_vesdt_bp.route('/', methods=['GET'])
# @login_required
def index():
    df_stakedao_vesdt = app.config['df_stakedao_vesdt']
    df_stakedao_vesdt_known = app.config['df_stakedao_vesdt_known']
    df_stakedao_vesdt_agg = app.config['df_stakedao_vesdt_agg']
    df_stakedao_vesdt_decay_agg = app.config['df_stakedao_vesdt_decay_agg']

    # Filter Data
    local_df_stakedao_vesdt = df_stakedao_vesdt.sort_values('date').groupby(['provider']).tail(2)
    local_df_stakedao_vesdt = local_df_stakedao_vesdt.sort_values('date').groupby(['provider']).head(1)
    local_df_stakedao_vesdt = local_df_stakedao_vesdt.sort_values('locked_balance',  axis = 0, ascending = False)

    # Build chart
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_layout(
        title=f"StakeDAO veSDT Lock Efficiency",
        xaxis_title="Section Date",
        yaxis_title="SDT Balance",
        yaxis2_title="Efficiency",
    )
    fig = fig.add_trace(
        go.Scatter(
            x = df_stakedao_vesdt_decay_agg.checkpoint_date,
            y = df_stakedao_vesdt_decay_agg.total_effective_locked_balance / df_stakedao_vesdt_decay_agg.total_locked_balance, 
            name = "Efficiency",
            # line_color='black',
            # line_width=3,
            # line_shape='hvh',

        ),
        secondary_y=True
    )

    fig = fig.add_trace(
        go.Scatter(
            x=df_stakedao_vesdt_decay_agg.checkpoint_date,
            y=df_stakedao_vesdt_decay_agg.total_locked_balance,
            name="Locked",
            fill='tozeroy',
            # line_shape='hvh',

            # color="pool_name"
        ),
        secondary_y=False
    )
    fig = fig.add_trace(
        go.Scatter(
            x = df_stakedao_vesdt_decay_agg.checkpoint_date,
            y = df_stakedao_vesdt_decay_agg.total_effective_locked_balance, 
            name = "Effectively Locked",
            fill='tozeroy',
            # line_width=3,
            # line_shape='hvh',

        ),
        # secondary_y=True
    )

    # fig.add_vline(x=dt.utcnow(), line_width=2, line_dash="dash", line_color="black" )
    fig.update_layout(autotypenumbers='convert types')

    fig.update_yaxes(range=[0,1], secondary_y=True)

    fig = format_plotly_figure(fig)
    # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)



    fig = px.line(df_stakedao_vesdt_agg,
                    x=df_stakedao_vesdt_agg['date'],
                    y=df_stakedao_vesdt_agg['balance_delta'],
                    # color='known_as',
                    # line_shape='linear',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    # fig.add_vline(x=dt.utcnow(), line_width=2, line_dash="dash", line_color="black")
    fig.update_layout(
        title=f"Locked veSDT Total Balance Changes",
            xaxis_title="Date",
            yaxis_title="Locked veSDT Balance Delta",
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

    
    fig = px.line(df_stakedao_vesdt_known,
                    x=df_stakedao_vesdt_known['date'],
                    y=df_stakedao_vesdt_known['locked_balance'],
                    color='known_as',
                    line_shape='hv',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    # fig.add_vline(x=dt.utcnow(), line_width=2, line_dash="dash", line_color="black")
    fig.update_layout(
        title=f"StakeDAO Locked veSDT Balances",
            xaxis_title="Date",
            yaxis_title="Locked veSDT Balance",
        #     legend_title="Legend Title",
        font=dict(        family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        ),
        # height= 1000,
    )

    # # Build Plotly object
    graphJSON3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

   # Build chart
    fig = px.bar(local_df_stakedao_vesdt,
                    x=local_df_stakedao_vesdt['final_lock_time'],
                    y=local_df_stakedao_vesdt['locked_balance'],
                    # color='provider',
                    title='Final Lock Time',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')
                      
    graphJSON4 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template(
        'index_stakedao_locked_vesdt.jinja2',
        title='StakeDAO Locked veSDT',
        template='stakedao-staked-vesdt-index',
        body="",
        # sum_current_votes = df_current_votes.total_vote_power.sum(),
        # sum_prior_votes = df_prior_votes.total_vote_power.sum(),
        # convex_agg_vote_locks = df_locker_agg_system,
        # convex_agg_epoch_vote_locks_current = df_locker_agg_current,
        stakedao_vesdt = local_df_stakedao_vesdt,
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
        graphJSON3 = graphJSON3,
        graphJSON4 = graphJSON4

    )



@stakedao_locked_vesdt_bp.route('/locker/<string:user>', methods=['GET'])
# @login_required
def show(user):
    df_stakedao_vesdt = app.config['df_stakedao_vesdt']
    df_stakedao_vesdt_decay = app.config['df_stakedao_vesdt_decay']

    # df_stakedao_vesdt_known = app.config['df_stakedao_vesdt_known']
    # df_stakedao_vesdt_agg = app.config['df_stakedao_vesdt_agg']

    
    # Filter Data
    local_df_stakedao_vesdt = df_stakedao_vesdt[df_stakedao_vesdt['provider'] == user]
    # local_df_locker = df_locker[df_locker['user'] == user]

    # local_df_locker_current = local_df_locker[local_df_locker['epoch_end'] >= dt.utcnow()]

    # local_df_gauge_votes = df_all_by_gauge.groupby(['voter', 'gauge_addr'], as_index=False).last()

    local_df_stakedao_vesdt_decay = df_stakedao_vesdt_decay[df_stakedao_vesdt_decay['provider'] == user]
    local_df_stakedao_vesdt_decay = local_df_stakedao_vesdt_decay.sort_values(['checkpoint', 'final_lock_time'],  axis = 0, ascending = False)
   
    # Build chart
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_layout(
        title=f"StakeDAO veSDT Lock Efficiency",
        xaxis_title="Section Date",
        yaxis_title="SDT Balance",
        yaxis2_title="Efficiency",
    )
    fig = fig.add_trace(
        go.Scatter(
            x = local_df_stakedao_vesdt_decay.checkpoint_date,
            y = local_df_stakedao_vesdt_decay.total_effective_locked_balance / local_df_stakedao_vesdt_decay.total_locked_balance, 
            name = "Efficiency",
            # line_color='black',
            # line_width=3,
            # line_shape='hvh',

        ),
        secondary_y=True
    )

    fig = fig.add_trace(
        go.Scatter(
            x=local_df_stakedao_vesdt_decay.checkpoint_date,
            y=local_df_stakedao_vesdt_decay.total_locked_balance,
            name="Locked",
            fill='tozeroy',
            # line_shape='hvh',

            # color="pool_name"
        ),
        secondary_y=False
    )
    fig = fig.add_trace(
        go.Scatter(
            x = local_df_stakedao_vesdt_decay.checkpoint_date,
            y = local_df_stakedao_vesdt_decay.total_effective_locked_balance, 
            name = "Effectively Locked",
            fill='tozeroy',
            # line_width=3,
            # line_shape='hvh',

        ),
        # secondary_y=True
    )

    # fig.add_vline(x=dt.utcnow(), line_width=2, line_dash="dash", line_color="black" )
    fig.update_layout(autotypenumbers='convert types')

    fig.update_yaxes(range=[0,1], secondary_y=True)

    fig = format_plotly_figure(fig)
    # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)



    fig = px.bar(local_df_stakedao_vesdt,
                    x=local_df_stakedao_vesdt['date'],
                    y=local_df_stakedao_vesdt['balance_delta'],
                    color='event_name',
                    # line_shape='linear',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    # fig.add_vline(x=dt.utcnow(), line_width=2, line_dash="dash", line_color="black")
    fig.update_layout(
        title=f"Locked veSDT Balance",
            xaxis_title="Date",
            yaxis_title="Locked veSDT Balance Delta",
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

    graphJSON3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        'show_stakedao_locked_vesdt.jinja2',
        title='StakeDAO Locked veSDT',
        template='stakedao-staked-vesdt-show',
        body="",
        # sum_current_votes = df_current_votes.total_vote_power.sum(),
        # sum_prior_votes = df_prior_votes.total_vote_power.sum(),
        # convex_agg_vote_locks = df_locker_agg_system,
        # convex_agg_epoch_vote_locks_current = df_locker_agg_current,
        stakedao_vesdt = local_df_stakedao_vesdt,
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2
    )