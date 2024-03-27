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

from app.utilities.utility import format_plotly_animation, format_plotly_figure

from .models import df_votium_v2


# Blueprint Configuration
votium_bounties_v2_bp = Blueprint(
    'votium_bounties_v2_bp', __name__,
    url_prefix='/votium_v2',
    template_folder='templates',
    static_folder='static'
)


@votium_bounties_v2_bp.route('/', methods=['GET'])
# @login_required
def index():
    # Filter Data
    df = great_filter(df_votium_v2, 'index', None)

    return render_template(
        'index_votium_v2.jinja2',
        title='Votium v2 Bounties',
        template='votium-index',
        body="",
        df_votium_v2 = df['df_votium'],
        df_current = df['current'],
        df_prior = df['prior'],
        graph_list = df['graph_list'],

    )

@votium_bounties_v2_bp.route('/bounty/<string:token_addr>', methods=['GET'])
# @login_required
def show_token(token_addr):
    # Filter Data
    df = great_filter(df_votium_v2, 'token', token_addr)
    
    return render_template(
        'show_token_votium_v2.jinja2',
        title='Votium v2 Bounty Token',
        template='votium-index',
        body="",
        df_votium_v2 = df['df_votium'],
        df_current = df['current'],
        df_prior = df['prior'],
        graph_list = df['graph_list'],

    )




@votium_bounties_v2_bp.route('/show/<string:gauge_addr>', methods=['GET'])
# @login_required
def show(gauge_addr):
    try:
        df_curve_gauge_registry = app.config['df_curve_gauge_registry']
    except: 
        from app.curve.gauges import df_curve_gauge_registry
    # Filter Data
    # df_votium_v2

    local_df_curve_gauge_registry = df_curve_gauge_registry[
        df_curve_gauge_registry['gauge_addr'] == gauge_addr
        ]
    
    df = great_filter(df_votium_v2, 'gauge', gauge_addr)


    return render_template(
        'show_votium_v2.jinja2',
        title='Votium v2 Bounties',
        template='votium-show',
        body="",
        local_df_curve_gauge_registry = local_df_curve_gauge_registry,
        df_votium_v2 = df['df_votium'],
        df_current = df['current'],
        df_prior = df['prior'],
        graph_list = df['graph_list'],


    )






def great_filter(df, tag, target):
    if tag == 'index':
        if type(target) == list:
            pass
    elif tag == 'gauge':
        if type(target) == list:
            df = df[df['gauge_addr'].isin(target)]
        else:
            df = df[df['gauge_addr'] == target]
    elif tag == 'token':
        if type(target) == list:
            df = df[df['token'].isin(target)]
        else:
            df = df[df['token'] == target]

    # Filter Data
    graph_list = []

    if tag == 'index' or tag == 'token':
        if tag == 'index':
            # lots of gauges, less tokens
            color_target = 'token_symbol'
            alt_target = 'gauge_symbol'
        else:
            # one token, handful of gauges
            color_target = 'gauge_symbol'
            alt_target = 'token_symbol'
        """
        Bounty Value Compare Rounds
        """
        votium_rounds = df.votium_round.unique()
        votium_rounds.sort()
        current_round = votium_rounds[-1]
        prior_round = votium_rounds[-2]
        df_current_bounties = df[df['votium_round'] == current_round]
        df_prior_bounties = df[df['votium_round'] == prior_round]

        # # Build chart
        fig = px.pie(df_prior_bounties, 
                    values=df_prior_bounties['bounty_value'],
                    names=df_prior_bounties['gauge_symbol'],
                    title=f"Bounty Value by Gauge: Round {prior_round}",
                    # hover_data=['gauge_addr'], labels={'gauge_addr':'gauge_addr'}
                    )
        fig.update_traces(textposition='inside', textinfo='percent')  # percent+label
            # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig.update_layout(autotypenumbers='convert types')
        fig = format_plotly_figure(fig)

        # # Build Plotly object
        graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))


        # # Build chart
        fig = px.pie(df_current_bounties, 
                    values=df_current_bounties['bounty_value'],
                    names=df_current_bounties['gauge_symbol'],
                    title=f"Bounty Value by Gauge: Round {current_round}",
                    hover_data=['gauge_addr'], labels={'gauge_addr':'gauge_addr'}
                    )
        fig.update_traces(textposition='inside', textinfo='percent')  # percent+label
            # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig.update_layout(autotypenumbers='convert types')
        fig = format_plotly_figure(fig)

        # # Build Plotly object
        graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

        """
        Animation
        """
        local_df = df.sort_values(['votium_round', 'total_vote_power', 'relative_vote_power'], ascending = False)
        fig = px.scatter(local_df, 
                    x="vecrv_per_bounty", 
                    y="relative_vote_power",
                    animation_frame="votium_round", 
                    animation_group="gauge_addr",
                    # size="bounty_value", 
                    color=color_target, 
                    hover_name=alt_target,
                    # log_x=True, 
                    # size_max=60,
                    # height=600,
                    title ="Total Vote Power vs Votes Per Dollar",
                    labels={
                            "votes_per_dollar": "Votes / Dollar",
                            "relative_vote_power": "Vote Power",
                            "token_symbol": "Bounty Token",
                            "gauge_symbol": "Gauge Symbol"
                        },
                    range_x=[50,1000],
                    range_y=[0,local_df.relative_vote_power.max()*1.1],
            )

        fig = format_plotly_figure(fig, 600)
        fig = format_plotly_animation(fig)
        # fig.layout['sliders'][0]['active'] = len(votium_rounds) - 1

        graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

        """
        Box Compare 4 weeks back
        """
        last_x_rounds = 4
        local_df = local_df[local_df['votium_round'] >= local_df.votium_round.max()-last_x_rounds+1]
        local_df.sort_values(['bounty_value', 'votium_round', 'gauge_symbol'])
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # fig = go.Figure()
        fig.update_layout(
            title=f"Bounty (USD) vs Vote Comparison: Last {last_x_rounds} Votium Rounds",
            xaxis_title="Gauge Symbol",
            yaxis_title="Liquidity (USD) or Votes (veCRV)",
            yaxis2_title='Liquidity (USD) / Votes',
            height=600
        #     legend_title="Legend Title",
        )

        fig = fig.add_trace(
            go.Box(
                x=local_df[color_target],
                y=local_df.bounty_value,
                name="Bounty_Value",
                # marker_color="blue"
            ),
            secondary_y=False

        )

        fig = fig.add_trace(
            go.Box(
                x = local_df[color_target],
                y = local_df.vecrv_per_bounty, 
                name = "Votes / Bounty Value",
                marker_color="grey",

            ),
            secondary_y=True
        )

        fig.update_yaxes(rangemode='nonnegative', secondary_y=False)
        fig.update_yaxes(rangemode='tozero', secondary_y=True)
        fig.update_yaxes(range=[0,1000], secondary_y=True)
        # fig = format_plotly_figure(fig, 600)

        graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))
    

        """
        Bar Pure Vote Power And Bounties
        """

        fig = px.bar(df,
                        x=df['votium_round'],
                        y=df['relative_vote_power'],
                        color=color_target,
                        title='Relative Vote Power Per Round',
                        # facet_row=facet_row,
                        # facet_col_wrap=facet_col_wrap
                        )
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig.update_layout(autotypenumbers='convert types')
        fig = format_plotly_figure(fig)

        # Build Plotly object
        graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))


        # # Build chart
        fig = px.bar(df,
                        x=df['votium_round'],
                        y=df['bounty_value'],
                        color=color_target,
                        title='Bounties (USD) per round',
                        # facet_row=facet_row,
                        # facet_col_wrap=facet_col_wrap
                        )
        fig = format_plotly_figure(fig)
        # # Build Plotly object 
        graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

    
    elif tag == 'gauge':
        df_current_bounties = []
        df_prior_bounties = []
        """
        Bar Pure Vote Power And Bounties
        """
        fig = px.bar(df,
                        x=df['votium_round'],
                        y=df['relative_vote_power'],
                        color='token_symbol',
                        title='Vote Power Per Round',
                        # facet_row=facet_row,
                        # facet_col_wrap=facet_col_wrap
                        )
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig.update_layout(autotypenumbers='convert types')

        # Build Plotly object
        graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

        # # Build chart
        fig = px.bar(df,
                        x=df['votium_round'],
                        y=df['bounty_value'],
                        color='token_symbol',
                        # line_shape='hv',
                        title='Bounty Value Per Round',
                        # facet_row=facet_row,
                        # facet_col_wrap=facet_col_wrap
                        )

        # # Build Plotly object
        graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

    return { 'df_votium': df,
            'current': df_current_bounties,
            'prior': df_prior_bounties,
            'graph_list': graph_list
            }
