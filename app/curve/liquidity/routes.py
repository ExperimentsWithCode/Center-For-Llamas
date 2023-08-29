from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for
# from flask_login import current_user, login_required

from flask import Response
from flask import request

from datetime import datetime
import json
import plotly
import plotly.express as px

import plotly.graph_objects as go
from plotly.subplots import make_subplots


from .models import df_liquidity, df_processed_liquidity

# Blueprint Configuration
curve_liquidity_bp = Blueprint(
    'curve_liquidity_bp', __name__,
    url_prefix='/curve/liquidity',
    template_folder='templates',
    static_folder='static'
)


@curve_liquidity_bp.route('/', methods=['GET'])
# @login_required
def index():
    now = datetime.now()

    # Filter Data

    # local_df_gauge_votes = df_all_by_gauge.groupby(['voter', 'gauge_addr'], as_index=False).last()



    return render_template(
        'index_liqudity.jinja2',
        title='Curve Liqudity',
        template='liquidity-index',
        body="",
        df_processed_liquidity = df_processed_liquidity,

    )



@curve_liquidity_bp.route('/show/<string:gauge_addr>', methods=['GET'])
# @login_required
def show(gauge_addr):
    now = datetime.now()
    # local_df_gauge_votes = df_all_by_gauge.groupby(['voter', 'gauge_addr'], as_index=False).last()

    local_all_df_processed_liquidity = df_processed_liquidity[
        df_processed_liquidity['gauge_address'].str.contains(gauge_addr)
        ]

    local_all_df_processed_liquidity = local_all_df_processed_liquidity.sort_values(
        ["date", 'liquidity'], axis = 0, ascending = False
        )


    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_layout(
        title=f"Liquidity vs Votes Filtered By: {local_all_df_processed_liquidity.iloc[0]['pool_name']} ",
        #     xaxis_title="X Axis Title",
        #     yaxis_title="Y Axis Title",
        #     legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        ),
        height= 1000,
    )
    fig = fig.add_trace(
        go.Bar(
            x=local_all_df_processed_liquidity.date,
            y=local_all_df_processed_liquidity.liquidity,
            name="Liquidity",
            # color="pool_name"
        ),
        secondary_y=False
    )
    fig = fig.add_trace(
        go.Scatter(
            x = local_all_df_processed_liquidity.date,
            y = local_all_df_processed_liquidity.total_votes, 
            name = "Total Votes",
            line_shape='hvh',
            line_width=3,
        ),
        secondary_y=True
    )
    fig.update_layout(autotypenumbers='convert types')
    fig.update_yaxes(rangemode="tozero")

    

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_layout(
        title=f"Liquidity vs Votes Filtered By: {local_all_df_processed_liquidity.iloc[0]['pool_name']} [Native Units]",
        #     xaxis_title="X Axis Title",
        #     yaxis_title="Y Axis Title",
        #     legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        ),
        height= 1000,
    )
    fig = fig.add_trace(
        go.Bar(
            x=local_all_df_processed_liquidity.date,
            y=local_all_df_processed_liquidity.liquidity_native,
            name="Liquidity",
            # color="pool_name"
        ),
        secondary_y=False
    )
    fig = fig.add_trace(
        go.Scatter(
            x = local_all_df_processed_liquidity.date,
            y = local_all_df_processed_liquidity.total_votes, 
            name = "Total Votes",
            line_shape='hvh',
            line_width=3,
        ),
        secondary_y=True
    )
    fig.update_layout(autotypenumbers='convert types')
    fig.update_yaxes(rangemode="tozero")


    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template(
        'show_liquidity.jinja2',
        title='Curve Liqudity',
        template='liquidity-index',
        body="",
        local_all_df_processed_liquidity = local_all_df_processed_liquidity,
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,

    )



@curve_liquidity_bp.route('/filter/<string:filter_asset>', methods=['GET'])
# @login_required
def filter(filter_asset):
    
    now = dt.now().date() - timedelta(days=(1))
    print(now)
    print(filter_asset)
    local_all_df_processed_liquidity = df_processed_liquidity[
        df_processed_liquidity['tradeable_assets'].str.contains(filter_asset)
        ]

    local_df_processed_liquidity = local_df_processed_liquidity.sort_values(
        ["date", 'liquidity'], axis = 0, ascending = False
        )

    local_df_processed_liquidity.head(10)


    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # fig = go.Figure()
    fig.update_layout(
        title=f"Liquidity vs Votes  Filtered By: {filter_asset}",
    #     xaxis_title="X Axis Title",
    #     yaxis_title="Y Axis Title",
    #     legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        ),
        height= 1000,
    )
    fig = fig.add_trace(
        go.Bar(
            x=local_df_processed_liquidity.display_symbol,
            y=local_df_processed_liquidity.liquidity,
            name="Liquidity",
            # color="pool_name"
        ),
        secondary_y=False

    )
    fig = fig.add_trace(
        go.Scatter(
            x = local_df_processed_liquidity.display_symbol,
            y = local_df_processed_liquidity.total_votes, 
            name = "Total Votes",
            line_shape='hvh',
            # line_width=3,
            # color=df_vote_deltas.name,
            # marker_color="red"
            # layout_yaxis_range=[0,5]
        ),
        secondary_y=True
    )
    fig.update_yaxes(rangemode="tozero")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # fig = go.Figure()
    fig.update_layout(
        title=f"Liquidity vs Votes  Filtered By: {filter_asset}",
    #     xaxis_title="X Axis Title",
    #     yaxis_title="Y Axis Title",
    #     legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        ),
        height= 1000,
    )
    fig = fig.add_trace(
        go.Bar(
            x=local_df_processed_liquidity.display_symbol,
            y=local_df_processed_liquidity.liquidity_native,
            name="Liquidity",
            # color="pool_name"
        ),
        secondary_y=False

    )
    fig = fig.add_trace(
        go.Scatter(
            x = local_df_processed_liquidity.display_symbol,
            y = local_df_processed_liquidity.total_votes, 
            name = "Total Votes",
            line_shape='hvh',
            # line_width=3,
            # color=df_vote_deltas.name,
            # marker_color="red"
            # layout_yaxis_range=[0,5]
        ),
        secondary_y=True
    )
    fig.update_yaxes(rangemode="tozero")
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template(
        'show_liqudity.jinja2',
        title='Curve Gauge Rounds',
        template='liquidity-show',
        body="",
        df_processed_liquidity = local_df_processed_liquidity,
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,



    )