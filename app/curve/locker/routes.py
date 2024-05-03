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


from app.utilities.utility import (
    format_plotly_figure,
    get_lock_diffs,
    get_now,
    get_address_profile
)
# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# from matplotlib.figure import Figure
# import io

from app.curve.locker.aggregators import get_ve_locker_decay_agg, get_ve_locker_agg, get_ve_locker_agg_known

from app.curve.locker.models import get_lock_diffs 

# Blueprint Configuration
curve_locker_vecrv_bp = Blueprint(
    'curve_locker_vecrv_bp', __name__,
    url_prefix='/stakedao/staked_vecrv',
    template_folder='templates',
    static_folder='static'
)



@curve_locker_vecrv_bp.route('/', methods=['GET'])
# @login_required
def index():
    df_curve_vecrv = app.config['df_curve_vecrv']
    # df_curve_vecrv_known = app.config['df_curve_vecrv_known']
    df_curve_vecrv_agg = get_ve_locker_agg(df_curve_vecrv)
    df_curve_vecrv_decay = app.config['df_curve_vecrv_decay']
    df_curve_vecrv_decay_agg = get_ve_locker_decay_agg(df_curve_vecrv_decay)


    # Filter Data
    local_df_curve_vecrv = df_curve_vecrv.sort_values('block_timestamp').groupby(['provider']).tail(1)
    # local_df_curve_vecrv = local_df_curve_vecrv.sort_values('date').groupby(['provider']).head(1)
    local_df_curve_vecrv = local_df_curve_vecrv.sort_values('locked_balance',  axis = 0, ascending = False)
    local_df_curve_vecrv = local_df_curve_vecrv[local_df_curve_vecrv['final_lock_time'] > get_now()]

    # Fancy Decay
    processed_known_decay = df_curve_vecrv_decay[
        ['known_as', 'checkpoint_timestamp', 'total_locked_balance', 'total_effective_locked_balance']].groupby([
            'checkpoint_timestamp', 'known_as',
        ]).agg(
        total_locked_balance=pd.NamedAgg(column='total_locked_balance', aggfunc=sum),
        total_effective_locked_balance=pd.NamedAgg(column='total_effective_locked_balance', aggfunc=sum),

        ).reset_index()

    # Build chart
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_layout(
        title=f"Curve veCRV Lock Efficiency",
        xaxis_title="Section Date",
        yaxis_title="CRV Balance",
        yaxis2_title="Efficiency",
    )
    fig = fig.add_trace(
        go.Scatter(
            x = df_curve_vecrv_decay_agg.checkpoint_timestamp,
            y = df_curve_vecrv_decay_agg.total_effective_locked_balance / df_curve_vecrv_decay_agg.total_locked_balance, 
            name = "Efficiency",
            # line_color='black',
            # line_width=3,
            # line_shape='hvh',

        ),
        secondary_y=True
    )

    fig = fig.add_trace(
        go.Scatter(
            x=df_curve_vecrv_decay_agg.checkpoint_timestamp,
            y=df_curve_vecrv_decay_agg.total_locked_balance,
            name="Locked",
            fill='tozeroy',
            # line_shape='hvh',

            # color="pool_name"
        ),
        secondary_y=False
    )
    fig = fig.add_trace(
        go.Scatter(
            x = df_curve_vecrv_decay_agg.checkpoint_timestamp,
            y = df_curve_vecrv_decay_agg.total_effective_locked_balance, 
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



    fig = px.line(df_curve_vecrv_agg,
                    x=df_curve_vecrv_agg['checkpoint_timestamp'],
                    y=df_curve_vecrv_agg['balance_delta'],
                    # color='known_as',
                    # line_shape='linear',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    # fig.add_vline(x=dt.utcnow(), line_width=2, line_dash="dash", line_color="black")
    fig.update_layout(
        title=f"Locked vecrv Total Balance Changes",
            xaxis_title="Date",
            yaxis_title="Locked vecrv Balance Delta",
        #     legend_title="Legend Title",
        # height= 1000,
    )
    fig = format_plotly_figure(fig)
    # # Build Plotly object
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    
    fig = px.line(processed_known_decay,
                    x=processed_known_decay['checkpoint_timestamp'],
                    y=processed_known_decay['total_effective_locked_balance'],
                    color='known_as',
                    line_shape='hv',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    # fig.add_vline(x=dt.utcnow(), line_width=2, line_dash="dash", line_color="black")
    fig.update_layout(
        title=f"Curve Locked veCRV Balances",
            xaxis_title="Date",
            yaxis_title="Locked veCRV Balance",
        #     legend_title="Legend Title",
        )
    fig = format_plotly_figure(fig)

    # # Build Plotly object
    graphJSON3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

   # Build chart
    fig = px.bar(local_df_curve_vecrv,
                    x=local_df_curve_vecrv['final_lock_time'],
                    y=local_df_curve_vecrv['locked_balance'],
                    # color='provider',
                    title='Final Lock Time',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    # fig.add_vline(x=dt.utcnow(), line_width=2, line_dash="dash", line_color="black")
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')
    fig = format_plotly_figure(fig)        
    graphJSON4 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template(
        'index_curve_locked_vecrv.jinja2',
        title='Curve - Locked veCRV - System',
        template='curve-locked-vecrv-index',
        body="",
        # sum_current_votes = df_current_votes.total_vote_power.sum(),
        # sum_prior_votes = df_prior_votes.total_vote_power.sum(),
        # convex_agg_vote_locks = df_locker_agg_system,
        # convex_agg_epoch_vote_locks_current = df_locker_agg_current,
        curve_vecrv = local_df_curve_vecrv,
        total_locked = df_curve_vecrv_decay_agg.iloc[-1]['total_locked_balance'],
        effectively_locked = df_curve_vecrv_decay_agg.iloc[-1]['total_effective_locked_balance'],
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
        graphJSON3 = graphJSON3,
        graphJSON4 = graphJSON4

    )



@curve_locker_vecrv_bp.route('/locker/<string:user>', methods=['GET'])
# @login_required
def show(user):
    df_curve_vecrv = app.config['df_curve_vecrv']
    df_curve_vecrv_decay = app.config['df_curve_vecrv_decay']
    # df_curve_vecrv_agg = app.config['df_curve_vecrv_agg']

    
    # Filter Data
    local_df_curve_vecrv = df_curve_vecrv[df_curve_vecrv['provider'] == user]
    local_df_curve_vecrv = local_df_curve_vecrv.sort_values(['block_timestamp', 'final_lock_time'],  axis = 0, ascending = False)

    local_df_curve_vecrv_decay = df_curve_vecrv_decay[df_curve_vecrv_decay['provider'] == user]
    local_df_curve_vecrv_decay = local_df_curve_vecrv_decay.sort_values(['checkpoint_id', 'final_lock_time'],  axis = 0, ascending = False)
    # local_df_locker = df_locker[df_locker['user'] == user]

    # local_df_locker_current = local_df_locker[local_df_locker['epoch_end'] >= dt.utcnow()]

    # local_df_gauge_votes = df_all_by_gauge.groupby(['voter', 'gauge_addr'], as_index=False).last()

    # Build chart
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_layout(
        title=f"Curve veCRV Lock Efficiency",
        xaxis_title="Section Date",
        yaxis_title="CRV Balance",
        yaxis2_title="Efficiency",
    )
    fig = fig.add_trace(
        go.Scatter(
            x = local_df_curve_vecrv_decay.checkpoint_timestamp,
            y = local_df_curve_vecrv_decay.total_effective_locked_balance / local_df_curve_vecrv_decay.total_locked_balance, 
            name = "Efficiency",
            # line_color='black',
            # line_width=3,
            # line_shape='hvh',

        ),
        secondary_y=True
    )

    fig = fig.add_trace(
        go.Scatter(
            x=local_df_curve_vecrv_decay.checkpoint_timestamp,
            y=local_df_curve_vecrv_decay.total_locked_balance,
            name="Locked",
            fill='tozeroy',
            # line_shape='hvh',

            # color="pool_name"
        ),
        secondary_y=False
    )
    fig = fig.add_trace(
        go.Scatter(
            x = local_df_curve_vecrv_decay.checkpoint_timestamp,
            y = local_df_curve_vecrv_decay.total_effective_locked_balance, 
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

    # fig = px.bar(local_df_curve_vecrv,
    #                 x=local_df_curve_vecrv['date'],
    #                 y=local_df_curve_vecrv['balance_delta'],
    #                 # color='known_as',
    #                 # line_shape='linear',
    #                 # facet_row=facet_row,
    #                 # facet_col_wrap=facet_col_wrap
    #                 )
    # # fig.add_vline(x=dt.utcnow(), line_width=2, line_dash="dash", line_color="black")
    # fig.update_layout(
    #     title=f"Locked vecrv Total Balance Changes",
    #         xaxis_title="Date",
    #         yaxis_title="Locked vecrv Balance Delta",
    #     #     legend_title="Legend Title",
    #     # height= 1000,
    # )
    # fig = format_plotly_figure(fig)

    # Calc remaining lock
    final_lock_time = local_df_curve_vecrv.iloc[0]['final_lock_time']
    diff_lock_weeks, diff_max_weeks = get_lock_diffs(final_lock_time)

    fig = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = diff_lock_weeks,
        mode = "gauge+number+delta",
        title = {'text': "Lock Efficiency (Weeks)"},
        delta = {'reference': diff_max_weeks},
        gauge = {'axis': {'range': [0, 225]},
                'steps' : [
                    {'range': [0, 52], 'color': "lightgray"},
                    {'range': [53, 104], 'color': "gray"},
                    {'range': [105, 156], 'color': "lightgray"},
                    {'range': [156, 208], 'color': "gray"},
                    {'range': [208, 225], 'color': "black"}],

                'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': diff_max_weeks}}))
    
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')
    fig = format_plotly_figure(fig)

    # # Build Plotly object
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # graphJSON3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        'show_curve_locked_vecrv.jinja2',
        title='Curve - Locked veCRV - User',
        template='stakedao-staked-vecrv-show',
        body="",
        actor_profile = get_address_profile(app.config['df_roles'], user),

        # sum_current_votes = df_current_votes.total_vote_power.sum(),
        # sum_prior_votes = df_prior_votes.total_vote_power.sum(),
        # convex_agg_vote_locks = df_locker_agg_system,
        # convex_agg_epoch_vote_locks_current = df_locker_agg_current,
        curve_vecrv = local_df_curve_vecrv,
        curve_vecrv_decay = local_df_curve_vecrv_decay,
        total_locked = local_df_curve_vecrv_decay.iloc[0]['total_locked_balance'],
        effectively_locked = local_df_curve_vecrv_decay.iloc[0]['total_effective_locked_balance'],

        graphJSON = graphJSON,
        graphJSON2 = graphJSON2
    )