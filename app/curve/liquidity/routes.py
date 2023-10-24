from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for
# from flask_login import current_user, login_required

from flask import Response
from flask import request

from datetime import datetime as dt
from datetime import timedelta

import json
import plotly
import plotly.express as px

import plotly.graph_objects as go
from plotly.subplots import make_subplots


from app.curve.liquidity.models import df_curve_liquidity, df_curve_liquidity_aggregates
from .forms import FilterLiquidityForm

try:
    # curve_gauge_registry = app.config['df_curve_gauge_registry']
    df_curve_gauge_registry = app.config['df_curve_gauge_registry']
    gauge_registry = app.config['gauge_registry']

except: 
    # from app.curve.gauges import df_curve_gauge_registry as curve_gauge_registry
    from app.curve.gauges.models import df_curve_gauge_registry, gauge_registry


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
    # now = dt.now()
    local_df_curve_liquidity_aggregates = df_curve_liquidity_aggregates.groupby(['pool_address', 'gauge_addr'], as_index=False).last()
    # Filter Data

    # local_df_gauge_votes = df_all_by_gauge.groupby(['voter', 'gauge_addr'], as_index=False).last()

    return render_template(
        'index_liqudity.jinja2',
        title='Curve Liqudity',
        template='liquidity-index',
        body="",
        df_curve_liquidity_aggregates = local_df_curve_liquidity_aggregates,

    )



@curve_liquidity_bp.route('/show/<string:gauge_addr>', methods=['GET'])
# @login_required
def show(gauge_addr):
    now = dt.now()
    # local_df_gauge_votes = df_all_by_gauge.groupby(['voter', 'gauge_addr'], as_index=False).last()

    local_df_curve_gauge_registry = df_curve_gauge_registry[df_curve_gauge_registry['gauge_addr'] == gauge_addr]
    local_all_df_curve_liquidity = df_curve_liquidity[
        df_curve_liquidity['gauge_addr'].str.contains(gauge_addr)
        ]

    local_all_df_curve_liquidity = local_all_df_curve_liquidity.sort_values(
        ["date", 'liquidity'], axis = 0, ascending = False
        )
    
    local_agg_df_curve_liquidity = df_curve_liquidity_aggregates[
        df_curve_liquidity_aggregates['gauge_addr'].str.contains(gauge_addr)
        ]

    local_agg_df_curve_liquidity = local_agg_df_curve_liquidity.sort_values(
        ["date", 'liquidity'], axis = 0, ascending = True
        )

    if len(local_all_df_curve_liquidity) > 0:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.update_layout(
            title=f"Liquidity vs Votes Filtered By: {local_agg_df_curve_liquidity.iloc[0]['pool_name']} ",
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
                x=local_agg_df_curve_liquidity.date,
                y=local_agg_df_curve_liquidity.liquidity,
                name="Liquidity",
                # color="pool_name"
            ),
            secondary_y=False
        )
        fig = fig.add_trace(
            go.Scatter(
                x = local_agg_df_curve_liquidity.date,
                y = local_agg_df_curve_liquidity.total_votes, 
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
            title=f"Liquidity vs Votes Filtered By: {local_agg_df_curve_liquidity.iloc[0]['pool_name']} [Native Units]",
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
                x=local_agg_df_curve_liquidity.date,
                y=local_agg_df_curve_liquidity.liquidity_native,
                name="Liquidity",
                # color="pool_name"
            ),
            secondary_y=False
        )
        fig = fig.add_trace(
            go.Scatter(
                x = local_agg_df_curve_liquidity.date,
                y = local_agg_df_curve_liquidity.total_votes, 
                name = "Total Votes",
                line_shape='hvh',
                line_width=3,
            ),
            secondary_y=True
        )
        fig.update_layout(autotypenumbers='convert types')
        fig.update_yaxes(rangemode="tozero")


        graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        fig = px.bar(local_all_df_curve_liquidity, x="date", y="liquidity", color="token_symbol", title="Liquidity By Asset")
        graphJSON3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        fig = px.bar(local_all_df_curve_liquidity, x="date", y="liquidity_native", color="token_symbol", title="Native Liquidity By Asset")
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



@curve_liquidity_bp.route('/filter_by_asset/', methods=['GET', 'POST'])
# @login_required
def filter_by_asset():
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

    dates_list = df_curve_liquidity_aggregates.date.unique()
    dates_list.sort()
    compare_date = dates_list[-1 -(days_back)]
    # filter by asset and head/tail
    # local_df_curve_liquidity = get_liquidity_comparison(df_curve_liquidity, filter_asset)
    # Filter to current date
    local_df = df_curve_liquidity_aggregates[df_curve_liquidity_aggregates['date'] == compare_date]

    # filter by asset 
    if filter_asset:
        local_df = local_df[local_df['token_symbol'].str.contains(filter_asset)]

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

    local_df = local_df.sort_values(['date', 'liquidity'], axis = 0, ascending = False )
    # filter head & tail
    local_df_curve_liquidity = local_df.head(head).tail(tail)

    df_tradeable_assets = df_curve_liquidity_aggregates[
            ['display_name', 'token_symbol', 'gauge_addr', 'liquidity', 'has_price']
        ].groupby('display_name').tail(1)
    df_tradeable_assets.sort_values('liquidity', axis=0, ascending = False)

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
        height= 1000,
    )
    fig = fig.add_trace(
        go.Bar(
            x=local_df_curve_liquidity.display_symbol,
            y=local_df_curve_liquidity.liquidity,
            name="Liquidity",
            # color="pool_name"
        ),
        secondary_y=False

    )
    fig = fig.add_trace(
        go.Scatter(
            x = local_df_curve_liquidity.display_symbol,
            y = local_df_curve_liquidity.total_votes, 
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
        height= 1000,
    )
    fig = fig.add_trace(
        go.Bar(
            x=local_df_curve_liquidity.display_symbol,
            y=local_df_curve_liquidity.liquidity_native,
            name="Liquidity",
            # color="pool_name"
        ),
        secondary_y=False,

    )
    fig = fig.add_trace(
        go.Scatter(
            x = local_df_curve_liquidity.display_symbol,
            y = local_df_curve_liquidity.total_votes, 
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