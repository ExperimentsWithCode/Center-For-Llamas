from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for
# from flask_login import current_user, login_required

# from flask import Response
# from flask import request

from datetime import datetime as dt
from datetime import timedelta

import json
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from app.utilities.utility import get_now, format_plotly_figure

from .forms import FilterLiquidityForm

# try:
#     # curve_gauge_registry = app.config['df_curve_gauge_registry']
#     df_curve_gauge_registry = app.config['df_curve_gauge_registry']
#     gauge_registry = app.config['gauge_registry']
#     df_curve_liquidity_aggregates = app.config['df_curve_liquidity_aggregates']
#     df_curve_liquidity = app.config['df_curve_liquidity']

# except: 
#     # from app.curve.gauges import df_curve_gauge_registry as curve_gauge_registry
#     from app.curve.gauges.models import df_curve_gauge_registry, gauge_registry
#     from app.curve.liquidity.models import df_curve_liquidity, df_curve_liquidity_aggregates#, df_curve_rebased_liquidity


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
    try:
        df_curve_liquidity_aggregates = app.config['df_curve_liquidity_aggregates']
    except: 
        from app.curve.liquidity.models import df_curve_liquidity_aggregates#, df_curve_rebased_liquidity

    # now = get_now()
    local_df_curve_liquidity_aggregates = df_curve_liquidity_aggregates.groupby(['pool_addr', 'gauge_addr'], as_index=False).last()
    local_df_curve_liquidity_aggregates = local_df_curve_liquidity_aggregates.sort_values('total_vote_power', ascending=False)
    # Filter Data

    graph_list = gen_top_figs(df_curve_liquidity_aggregates, 20, 5, 8)

    # local_df_gauge_votes = df_all_by_gauge.groupby(['voter', 'gauge_addr'], as_index=False).last()

    return render_template(
        'index_liqudity.jinja2',
        title='Curve Liqudity',
        template='liquidity-index',
        body="",
        df_curve_liquidity_aggregates = local_df_curve_liquidity_aggregates,
        graph_list=graph_list,

    )



@curve_liquidity_bp.route('/show/<string:gauge_addr>', methods=['GET'])
# @login_required
def show(gauge_addr):
    try:
        # curve_gauge_registry = app.config['df_curve_gauge_registry']
        df_curve_gauge_registry = app.config['df_curve_gauge_registry']
        # gauge_registry = app.config['gauge_registry']
        df_curve_liquidity_aggregates = app.config['df_curve_liquidity_aggregates']
        df_curve_liquidity = app.config['df_curve_liquidity']

    except: 
        # from app.curve.gauges import df_curve_gauge_registry as curve_gauge_registry
        from app.curve.gauges.models import df_curve_gauge_registry, gauge_registry
        from app.curve.liquidity.models import df_curve_liquidity, df_curve_liquidity_aggregates#, df_curve_rebased_liquidity

    # now = get_now()
    # local_df_gauge_votes = df_all_by_gauge.groupby(['voter', 'gauge_addr'], as_index=False).last()

    local_df_curve_gauge_registry = df_curve_gauge_registry[df_curve_gauge_registry['gauge_addr'] == gauge_addr]

    local_all_df_curve_liquidity = df_curve_liquidity[
        df_curve_liquidity['gauge_addr'].str.contains(gauge_addr)
        ]

    local_all_df_curve_liquidity = local_all_df_curve_liquidity.sort_values(
        ["block_timestamp", 'balance_usd'], axis = 0, ascending = False
        )
    
    local_agg_df_curve_liquidity = df_curve_liquidity_aggregates[
        df_curve_liquidity_aggregates['gauge_addr'].str.contains(gauge_addr)
        ]

    local_agg_df_curve_liquidity = local_agg_df_curve_liquidity.sort_values(
        ["block_timestamp", 'total_balance_usd'], axis = 0, ascending = True
        )
    local_chart_agg_filter = local_agg_df_curve_liquidity[local_agg_df_curve_liquidity['total_vote_power'] > 5000]

    if len(local_all_df_curve_liquidity) > 0:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.update_layout(
            title=f"Liquidity (USD) and Votes: {local_agg_df_curve_liquidity.iloc[0]['gauge_symbol']} ",
            #     xaxis_title="X Axis Title",
            #     yaxis_title="Y Axis Title",
            #     legend_title="Legend Title",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="RebeccaPurple"
            ),
            # height= 1000,
        )
        fig = fig.add_trace(
            go.Box(
                x=local_agg_df_curve_liquidity.checkpoint_timestamp,
                y=local_agg_df_curve_liquidity.total_balance_usd,
                name="Liquidity",
                # color="pool_name"
            ),
            secondary_y=False
        )
        fig = fig.add_trace(
            go.Scatter(
                x = local_agg_df_curve_liquidity.checkpoint_timestamp,
                y = local_agg_df_curve_liquidity.total_vote_power, 
                name = "Total Votes",
                line_shape='hvh',
                # line_width=3,
            ),
            # secondary_y=True
        )
        fig.update_layout(autotypenumbers='convert types')
        fig.update_yaxes(rangemode="tozero")

        

        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.update_layout(
            title=f"Liquidity (USD) / Votes: {local_agg_df_curve_liquidity.iloc[0]['gauge_symbol']}",
            #     xaxis_title="X Axis Title",
            #     yaxis_title="Y Axis Title",
            #     legend_title="Legend Title",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="RebeccaPurple"
            ),
            # height= 1000,
        )
        fig = fig.add_trace(
            go.Box(
                x=local_chart_agg_filter.checkpoint_timestamp,
                y=local_chart_agg_filter.liquidity_usd_over_votes,
                name="Liquidity (USD) / Votes",
                # color="pool_name"
            ),
            secondary_y=False
        )
        # fig = fig.add_trace(
        #     go.Box(
        #         x = local_agg_df_curve_liquidity.checkpoint_timestamp,
        #         y = local_agg_df_curve_liquidity.total_vote_power, 
        #         name = "Total Votes",
        #         # line_shape='hvh',
        #         # line_width=3,
        #     ),
        #     # secondary_y=True
        # )
        fig.update_layout(autotypenumbers='convert types')
        fig.update_yaxes(rangemode="tozero")


        graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        fig = px.bar(local_all_df_curve_liquidity, x="block_timestamp", y="balance_usd", color="symbol", title="Liquidity (USD) By Asset")
        graphJSON3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        fig = px.bar(local_all_df_curve_liquidity, x="block_timestamp", y="balance", color="symbol", title="Liquidity (Native) By Asset")
        graphJSON4 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    else:
        graphJSON = None
        graphJSON2 = None

    return render_template(
        'show_liquidity.jinja2',
        title='Curve Liqudity',
        template='liquidity-index',
        body="",
        local_all_df_curve_liquidity = local_all_df_curve_liquidity,
        local_df_curve_gauge_registry = local_df_curve_gauge_registry,
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
        graphJSON3 = graphJSON3,
        graphJSON4 = graphJSON4


    )


# @curve_liquidity_bp.route('/show/based/<string:gauge_addr>', methods=['GET'])
# # @login_required
# def show_based(gauge_addr):
#     now = get_now()
#     # local_df_gauge_votes = df_all_by_gauge.groupby(['voter', 'gauge_addr'], as_index=False).last()

#     local_df_curve_gauge_registry = df_curve_gauge_registry[df_curve_gauge_registry['gauge_addr'] == gauge_addr]
#     local_all_df_curve_liquidity = df_curve_rebased_liquidity[
#         df_curve_rebased_liquidity['gauge_addr'].str.contains(gauge_addr)
#         ]

#     local_all_df_curve_liquidity = local_all_df_curve_liquidity.sort_values(
#         ["block_timestamp", 'balance_usd'], axis = 0, ascending = False
#         )
    
#     local_agg_df_curve_liquidity = df_curve_liquidity_aggregates[
#         df_curve_liquidity_aggregates['gauge_addr'].str.contains(gauge_addr)
#         ]

#     local_agg_df_curve_liquidity = local_agg_df_curve_liquidity.sort_values(
#         ["block_timestamp", 'total_balance_usd'], axis = 0, ascending = True
#         )
#     local_chart_agg_filter = local_agg_df_curve_liquidity[local_agg_df_curve_liquidity['total_vote_power'] > 5000]

#     if len(local_all_df_curve_liquidity) > 0:
#         fig = make_subplots(specs=[[{"secondary_y": True}]])
#         fig.update_layout(
#             title=f"Liquidity (USD) and Votes: {local_agg_df_curve_liquidity.iloc[0]['gauge_symbol']} ",
#             #     xaxis_title="X Axis Title",
#             #     yaxis_title="Y Axis Title",
#             #     legend_title="Legend Title",
#             font=dict(
#                 family="Courier New, monospace",
#                 size=18,
#                 color="RebeccaPurple"
#             ),
#             # height= 1000,
#         )
#         fig = fig.add_trace(
#             go.Box(
#                 x=local_agg_df_curve_liquidity.checkpoint_timestamp,
#                 y=local_agg_df_curve_liquidity.total_balance_usd,
#                 name="Liquidity",
#                 # color="pool_name"
#             ),
#             secondary_y=False
#         )
#         fig = fig.add_trace(
#             go.Box(
#                 x = local_agg_df_curve_liquidity.checkpoint_timestamp,
#                 y = local_agg_df_curve_liquidity.total_vote_power, 
#                 name = "Total Votes",
#                 # line_shape='hvh',
#                 # line_width=3,
#             ),
#             # secondary_y=True
#         )
#         fig.update_layout(autotypenumbers='convert types')
#         fig.update_yaxes(rangemode="tozero")

        

#         graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

#         fig = make_subplots(specs=[[{"secondary_y": True}]])
#         fig.update_layout(
#             title=f"Liquidity (USD) / Votes: {local_agg_df_curve_liquidity.iloc[0]['gauge_symbol']}",
#             #     xaxis_title="X Axis Title",
#             #     yaxis_title="Y Axis Title",
#             #     legend_title="Legend Title",
#             font=dict(
#                 family="Courier New, monospace",
#                 size=18,
#                 color="RebeccaPurple"
#             ),
#             # height= 1000,
#         )
#         fig = fig.add_trace(
#             go.Box(
#                 x=local_chart_agg_filter.checkpoint_timestamp,
#                 y=local_chart_agg_filter.liquidity_usd_over_votes,
#                 name="Liquidity (USD) / Votes",
#                 # color="pool_name"
#             ),
#             secondary_y=False
#         )
#         # fig = fig.add_trace(
#         #     go.Box(
#         #         x = local_agg_df_curve_liquidity.checkpoint_timestamp,
#         #         y = local_agg_df_curve_liquidity.total_vote_power, 
#         #         name = "Total Votes",
#         #         # line_shape='hvh',
#         #         # line_width=3,
#         #     ),
#         #     # secondary_y=True
#         # )
#         fig.update_layout(autotypenumbers='convert types')
#         fig.update_yaxes(rangemode="tozero")


#         graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

#         fig = px.bar(local_all_df_curve_liquidity, x="block_timestamp", y="balance_usd", color="symbol", title="Liquidity (USD) By Asset")
#         graphJSON3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

#         fig = px.bar(local_all_df_curve_liquidity, x="block_timestamp", y="balance", color="symbol", title="Liquidity (Native) By Asset")
#         graphJSON4 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

#     else:
#         graphJSON = None
#         graphJSON2 = None
#         graphJSON3 = None
#         graphJSON4 = None

#     return render_template(
#         'show_liquidity.jinja2',
#         title='Curve Liqudity',
#         template='liquidity-index',
#         body="",
#         local_all_df_curve_liquidity = local_all_df_curve_liquidity,
#         local_df_curve_gauge_registry = local_df_curve_gauge_registry,
#         graphJSON = graphJSON,
#         graphJSON2 = graphJSON2,
#         graphJSON3 = graphJSON3,
#         graphJSON4 = graphJSON4


#     )

@curve_liquidity_bp.route('/filter_by_asset/', methods=['GET', 'POST'])
# @login_required
def filter_by_asset():
    try:
        # curve_gauge_registry = app.config['df_curve_gauge_registry']
        df_curve_gauge_registry = app.config['df_curve_gauge_registry']
        gauge_registry = app.config['gauge_registry']
        df_curve_liquidity_aggregates = app.config['df_curve_liquidity_aggregates']
        # df_curve_liquidity = app.config['df_curve_liquidity']
    except: 
        # from app.curve.gauges import df_curve_gauge_registry as curve_gauge_registry
        from app.curve.gauges.models import df_curve_gauge_registry, gauge_registry
        from app.curve.liquidity.models import df_curve_liquidity_aggregates

    form = FilterLiquidityForm()
    address_list = []
    placeholder_list = [{'gauge_addr': '', 'delete': False}] *5
    if form.validate_on_submit():
        filter_asset= form.filter_asset.data if form.filter_asset.data else ''
        head = int(form.head.data if form.head.data else 20)
        tail  = int(form.tail.data if form.tail.data else 20)
        source = form.source.data if form.source.data else ''
        days_back = form.days_back.data if form.days_back.data or form.days_back.data >= 0  else 1
        address_list_data = [] # placeholder 
        for entry in form.gauge_address_list.data:
            if not entry['delete'] and not entry['gauge_addr'] == '':
                address_list_data.append({'gauge_addr': entry['gauge_addr'].lower(), 'delete': False}) 
                address_list.append(entry['gauge_addr'].lower())
        address_list_data += placeholder_list
    else:
        filter_asset=None
        head = 20
        tail = 20
        source = ''
        days_back = 1
        address_list_data = placeholder_list
    form.process(data={'gauge_address_list': address_list_data, 
                       'head':head, 
                       'tail': tail, 
                       'filter_asset':filter_asset,
                       'source': source,
                       'days_back': days_back
                       })

    block_timestamp_list = df_curve_liquidity_aggregates.block_timestamp.unique()
    compare_point = block_timestamp_list[-1 -(days_back)]

    # Filter to current date
    local_df = df_curve_liquidity_aggregates[df_curve_liquidity_aggregates['block_timestamp'] == compare_point]

    # filter by asset 
    if filter_asset:
        local_df = local_df[local_df['tradable_assets'].str.contains(filter_asset)]

        selection = [filter_asset]
        mask = local_df.tradable_assets.apply(lambda x: any(item for item in selection if item in x))
        local_df = local_df[mask]    
        
    # filter by source
    if source:
        local_registry =  df_curve_gauge_registry[df_curve_gauge_registry['source'] == source]
        local_df = local_df[
            local_df['gauge_addr'].isin(local_registry.gauge_addr)
        ]
    
    # filter by inclusion list
    if len(address_list) > 0:
        local_df = local_df[
            local_df['gauge_addr'].isin(address_list)
            ]

    local_df = local_df.sort_values(['block_timestamp', 'total_balance_usd'], axis = 0, ascending = False )
    local_df['display_symbol'] = local_df.gauge_addr.apply(gauge_registry.get_gauge_display_name)
    # filter head & tail
    local_df_curve_liquidity = local_df.head(head).tail(tail)

    df_tradeable_assets = df_curve_liquidity_aggregates[
            ['tradable_assets', 'gauge_addr', 'gauge_name', 'gauge_symbol', 'total_balance_usd']
        ].groupby('gauge_addr').tail(1)
    
    df_tradeable_assets.sort_values('total_balance_usd', axis=0, ascending = False)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # fig = go.Figure()
    fig.update_layout(
        title=f"(USD) Liquidity vs Votes  Filtered By: {filter_asset}",
    #     xaxis_title="X Axis Title",
    #     yaxis_title="Y Axis Title",
    #     legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        ),
        # height= 1000,
    )
    fig = fig.add_trace(
        go.Bar(
            x=local_df_curve_liquidity.display_symbol,
            y=local_df_curve_liquidity.total_balance_usd,
            name="Liquidity",
            # color="pool_name"
        ),
        secondary_y=False

    )
    fig = fig.add_trace(
        go.Scatter(
            x = local_df_curve_liquidity.display_symbol,
            y = local_df_curve_liquidity.total_vote_power,
            name = "Total Votes",
            line_shape='hvh',
            # line_width=3,
            # color=df_vote_deltas.name,
            # marker_color="red"
            # layout_yaxis_range=[0,5]
        ),
        secondary_y=True
    )
    fig.update_yaxes(rangemode='nonnegative', secondary_y=False)
    fig.update_yaxes(rangemode='tozero', secondary_y=True)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # fig = go.Figure()
    fig.update_layout(
        title=f"(Native) Liquidity vs Votes  Filtered By: {filter_asset}",
    #     xaxis_title="X Axis Title",
    #     yaxis_title="Y Axis Title",
    #     legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        ),
        # height= 1000,
    )
    fig = fig.add_trace(
        go.Bar(
            x=local_df_curve_liquidity.display_symbol,
            y=local_df_curve_liquidity.total_balance,
            name="Liquidity",
            # color="pool_name"
        ),
        secondary_y=False,

    )
    fig = fig.add_trace(
        go.Scatter(
            x = local_df_curve_liquidity.display_symbol,
            y = local_df_curve_liquidity.total_vote_power, 
            name = "Total Votes",
            line_shape='hvh',
            # line_width=3,
            # color=df_vote_deltas.name,
            # marker_color="red"
            # layout_yaxis_range=[0,5]
        ),
        secondary_y=True,
    )
    fig.update_yaxes(rangemode='nonnegative', secondary_y=False)
    fig.update_yaxes(rangemode='tozero', secondary_y=True)
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template(
        'filter_liquidity.jinja2',
        title='Curve Liquidity To Votes Comparison',
        template='liquidity-show',
        body="",
        form=form,
        gauge_registry = gauge_registry,
        filter_asset = filter_asset,
        head = head,
        tail = tail,
        source = source,
        days_back = days_back,
        df_curve_liquidity = local_df_curve_liquidity,
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
        df_tradeable_assets = df_tradeable_assets

    )

def chart_liquidity_and_vote_aggs(df, head, tail, back_track ):
    # local_df = last_4_top_20.sort_values('liquidity_usd_over_votes', ascending=False)
    local_df = df.sort_values('total_vote_power', ascending=False)

    filter_asset = f"Top {head-tail}-{head} Vote Power Past {back_track} Checkpoints"
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # fig = go.Figure()
    fig.update_layout(
        title=f"(USD) Liquidity / Votes Filtered By: {filter_asset}",
        xaxis_title="Gauge Symbol",
        yaxis_title="Liquidity (USD) or Votes (veCRV)",
        yaxis2_title='Liquidity (USD) / Votes'
    #     legend_title="Legend Title",
    )


    fig = fig.add_trace(
        go.Box(
            x=local_df.gauge_symbol,
            y=local_df.total_balance_usd,
            name="Liquidity",
            # color="pool_name"
            # marker_color="blue"

        ),
        secondary_y=False

    )
    fig = fig.add_trace(
        go.Box(
            x = local_df.gauge_symbol,
            y = local_df.total_vote_power, 
            name = "Total Votes",
            # points='all'
            # line_shape='hvh',
            # line_width=3,
            # color=df_temp_vote_deltas.name,
            # marker_color="red"
            # layout_yaxis_range=[0,5]
        ),
        # secondary_y=True
    )

    fig = fig.add_trace(
        go.Box(
            x = local_df.gauge_symbol,
            y = local_df.liquidity_usd_over_votes, 
            name = "Liquidity / Votes",
            # line_shape='hvh',
            # line_width=3,
            # color=df_vote_deltas.name,
            marker_color="grey",
            visible='legendonly'
            # layout_yaxis_range=[0,5]
        ),
        secondary_y=True
    )

    fig.update_yaxes(rangemode='nonnegative', secondary_y=False)
    fig.update_yaxes(rangemode='tozero', secondary_y=True)
    # fig.update_yaxes(range=[0,10], secondary_y=True)
    # fig = format_plotly_figure(fig, 800)
    return fig

def gen_top_figs(df, max_size, interval, back_track=8, convert_to_json=True):
    # Get current Votes
    current_votes = df[
        df['checkpoint_id'] == df.checkpoint_id.max()
        ].sort_values(['total_vote_power','checkpoint_id', 'gauge_addr'], ascending = False)
    # Collapse to single vote power per gauge
    ranked_voters = current_votes.groupby(
            ['checkpoint_id', 'gauge_addr', 'gauge_name', 'gauge_symbol']
        ).agg(
        total_vote_power=pd.NamedAgg(column='total_vote_power', aggfunc=lambda x: np.mean(x)),
        # lock_count=pd.NamedAgg(column='lock_count', aggfunc=sum)
        ).reset_index()
    # Rank
    ranked_voters['vote_ranking'] = ranked_voters.groupby(['checkpoint_id'])['total_vote_power'].rank('average')
    ranked_voters = ranked_voters.sort_values('vote_ranking', ascending=False)
    back_tracked_data = df[
        df['checkpoint_id'] == df.checkpoint_id.max() - back_track
        ].sort_values(['total_vote_power','checkpoint_id', 'gauge_addr'], ascending = False)
    
    figs = []
    head = 0
    while head < max_size:
        head += interval
        these_gauge_addrs = ranked_voters.head(head).tail(interval)
        # print(len(these_gauge_addrs))
        # print(len(these_gauge_addrs.gauge_symbol.unique()))

        this_df = back_tracked_data[back_tracked_data['gauge_addr'].isin(these_gauge_addrs.gauge_addr.unique())]
        this_df = this_df.sort_values(['checkpoint_id', 'total_vote_power'], ascending=False)
        this_fig = chart_liquidity_and_vote_aggs(this_df, head, interval, back_track)
        if convert_to_json:
            figs.append(json.dumps(this_fig, cls=plotly.utils.PlotlyJSONEncoder))
        else:
            figs.append(this_fig)
    return figs
        