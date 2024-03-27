from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for
# from flask_login import current_user, login_required

from flask import Response
from flask import request

from datetime import datetime
import json
import plotly
import plotly.express as px

from .models import df_votium_bounty_formatted as df_bounty_formatted

# Blueprint Configuration
votium_bounties_bp = Blueprint(
    'votium_bounties_bp', __name__,
    url_prefix='/convex/votium',
    template_folder='templates',
    static_folder='static'
)


@votium_bounties_bp.route('/', methods=['GET'])
# @login_required
def index():
    # Filter Data

    # local_df_gauge_votes = df_bounty_formatted.groupby(['voter', 'gauge_addr'], as_index=False).last()
    # Build chart
    fig = px.bar(df_bounty_formatted,
                    x=df_bounty_formatted['checkpoint_timestamp'],
                    y=df_bounty_formatted['relative_vote_power'],
                    color='gauge_ref',
                    title='Vote Power Per Round',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # periods = df_meta_gauge_aggregate.this_period.unique()
    # periods.sort()
    # current_checkpoint = periods[-1]
    # prior_checkpoint = periods[-2]
    # df_current_votes = df_meta_gauge_aggregate[df_meta_gauge_aggregate['this_period'] == current_checkpoint]
    # df_prior_votes = df_meta_gauge_aggregate[df_meta_gauge_aggregate['this_period'] == prior_checkpoint]

    # # Build chart
    fig = px.bar(df_bounty_formatted,
                    x=df_bounty_formatted['checkpoint_timestamp'],
                    y=df_bounty_formatted['votes_per_dollar'],
                    color='gauge_ref',
                    title='Votes Per Dollar Bounties',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )

    # # Build Plotly object 
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)



    checkpoint_ids = df_bounty_formatted.checkpoint_id.unique()
    checkpoint_ids.sort()
    current_checkpoint = checkpoint_ids[-1]
    prior_checkpoint = checkpoint_ids[-3]
    df_current_bounties = df_bounty_formatted[df_bounty_formatted['checkpoint_id'] == current_checkpoint]
    df_prior_bounties = df_bounty_formatted[df_bounty_formatted['checkpoint_id'] == prior_checkpoint]


    # # Build chart
    fig = px.pie(df_current_bounties, 
                values=df_current_bounties['votes_per_dollar'],
                names=df_current_bounties['gauge_ref'],
                title=f"Prior Round Vote Distribution {current_checkpoint}",
                hover_data=['gauge_addr'], labels={'gauge_addr':'gauge_addr'}
                )
    fig.update_traces(textposition='inside', textinfo='percent')  # percent+label
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # # Build Plotly object
    graphJSON3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # # Build chart
    fig = px.pie(df_prior_bounties, 
                values=df_prior_bounties['votes_per_dollar'],
                names=df_prior_bounties['gauge_ref'],
                title=f"Prior Round Vote Distribution {prior_checkpoint}",
                # hover_data=['gauge_addr'], labels={'gauge_addr':'gauge_addr'}
                )
    fig.update_traces(textposition='inside', textinfo='percent')  # percent+label
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # # Build Plotly object
    graphJSON4 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # # Build chart
    fig = px.scatter(df_current_bounties, 
                    x="votes_per_dollar", 
                    y="relative_vote_power", 
                    # size="bounty_value", 
                    color="gauge_ref",
                    hover_name="gauge_ref", 
                    log_x=True, 
                    # size_max=60,
                    title ="Total Vote Power vs Votes Per Dollar",
                    labels={
                        "votes_per_dollar": "Votes / Dollar",
                        "relative_vote_power": "Vote Power",
                        "gauge_ref": "Gauge Bountied"
                    },
                    )
    
        # # Build Plotly object
    graphJSON5 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.scatter(df_prior_bounties, 
                    x="votes_per_dollar", 
                    y="relative_vote_power", 
                    # size="bounty_value", 
                    color="gauge_ref",
                    hover_name="gauge_ref", 
                    log_x=True, 
                    # size_max=60,
                    title ="Total Vote Power vs Votes Per Dollar",
                    labels={
                        "votes_per_dollar": "Votes / Dollar",
                        "relative_vote_power": "Vote Power",
                        "gauge_ref": "Gauge Bountied"
                    },
                    )
    
        # # Build Plotly object
    graphJSON6 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    fig = px.scatter(df_bounty_formatted, 
                x="votes_per_dollar", 
                y="relative_vote_power",
                animation_frame="checkpoint_timestamp", 
                animation_group="gauge_ref",
                # size="bounty_value", 
                color="gauge_ref", 
                hover_name="gauge_ref",
                log_x=True, 
                # size_max=60, 
                height=600,
                title ="Total Vote Power vs Votes Per Dollar",
                labels={
                     "votes_per_dollar": "Votes / Dollar",
                     "relative_vote_power": "Vote Power",
                     "gauge_ref": "Gauge Bountied"
                 },

                # range_x=[0,200], 
                # range_y=[0,15000000]
    )
    
    graphJSON7 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    fig = px.scatter(df_bounty_formatted, 
                x="votes_per_dollar", 
                y="relative_vote_power",
                animation_frame="checkpoint_timestamp", 
                animation_group="gauge_ref",
                # size="bounty_value", 
                color="token_symbol", 
                hover_name="gauge_ref",
                log_x=True, 
                # size_max=60,
                height=600,
                title ="Total Vote Power vs Votes Per Dollar",
                labels={
                     "votes_per_dollar": "Votes / Dollar",
                     "relative_vote_power": "Vote Power",
                     "token_symbol": "Bounty Token"
                 },

                # range_x=[0,200], 
                # range_y=[0,15000000]
    )
    
    graphJSON8 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        'index_votium.jinja2',
        title='Votium Bounties',
        template='votium-index',
        body="",
        df_bounty_formatted = df_bounty_formatted,
        df_current = df_current_bounties,
        df_prior = df_prior_bounties,
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
        graphJSON3 = graphJSON3,
        graphJSON4 = graphJSON4,
        graphJSON5 = graphJSON5,
        graphJSON6 = graphJSON6,
        graphJSON7 = graphJSON7,
        graphJSON8 = graphJSON8



    )



@votium_bounties_bp.route('/show/<string:gauge_ref>', methods=['GET'])
# @login_required
def show(gauge_ref):
    try:
        df_curve_gauge_registry = app.config['df_curve_gauge_registry']
    except: 
        from app.curve.gauges import df_curve_gauge_registry
    # Filter Data
    # df_bounty_formatted
    local_df_bounty_formatetd = df_bounty_formatted[df_bounty_formatted['gauge_ref'] == gauge_ref]
    local_df_curve_gauge_registry = df_curve_gauge_registry[
        df_curve_gauge_registry['gauge_addr'] == local_df_bounty_formatetd.iloc[0]['gauge_addr']
        ]

    # local_df_gauge_votes = df_bounty_formatted.groupby(['voter', 'gauge_addr'], as_index=False).last()
    # Build chart
    fig = px.bar(local_df_bounty_formatetd,
                    x=local_df_bounty_formatetd['checkpoint_timestamp'],
                    y=local_df_bounty_formatetd['relative_vote_power'],
                    color='token_symbol',
                    title='Vote Power Per Round',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # periods = df_meta_gauge_aggregate.this_period.unique()
    # periods.sort()
    # current_checkpoint = periods[-1]
    # prior_checkpoint = periods[-2]
    # df_current_votes = df_meta_gauge_aggregate[df_meta_gauge_aggregate['this_period'] == current_checkpoint]
    # df_prior_votes = df_meta_gauge_aggregate[df_meta_gauge_aggregate['this_period'] == prior_checkpoint]

    # # Build chart
    fig = px.line(local_df_bounty_formatetd,
                    x=local_df_bounty_formatetd['checkpoint_timestamp'],
                    y=local_df_bounty_formatetd['votes_per_dollar'],
                    # color='token_symbol',
                    line_shape='hv',
                    title='Votes Per Dollar Bounties',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )

    # # Build Plotly object
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)



    # periods = df_bounty_formatted.period.unique()
    # periods.sort()
    # current_checkpoint = periods[-1]
    # prior_checkpoint = periods[-2]
    # df_current_bounties = local_df_bounty_formatetd[local_df_bounty_formatetd['checkpoint_id'] == current_checkpoint]
    # df_prior_bounties = local_df_bounty_formatetd[local_df_bounty_formatetd['checkpoint_id'] == prior_checkpoint]


    # # # Build chart
    # fig = px.pie(df_current_bounties, 
    #             values=df_current_bounties['votes_per_dollar'],
    #             names=df_current_bounties['gauge_ref'],
    #             title=f"Prior Round Vote Distribution {current_checkpoint}",
    #             hover_data=['gauge_addr'], labels={'gauge_addr':'gauge_addr'}
    #             )
    # fig.update_traces(textposition='inside', textinfo='percent')  # percent+label
    #     # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    # fig.update_layout(autotypenumbers='convert types')

    # # # Build Plotly object
    # graphJSON3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # # # Build chart
    # fig = px.pie(df_prior_bounties, 
    #             values=df_prior_bounties['votes_per_dollar'],
    #             names=df_prior_bounties['gauge_ref'],
    #             title=f"Prior Round Vote Distribution {prior_checkpoint}",
    #             # hover_data=['gauge_addr'], labels={'gauge_addr':'gauge_addr'}
    #             )
    # fig.update_traces(textposition='inside', textinfo='percent')  # percent+label
    #     # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    # fig.update_layout(autotypenumbers='convert types')

    # # # Build Plotly object
    # graphJSON4 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        'show_votium.jinja2',
        title='Votium Bounties',
        template='votium-show',
        body="",
        local_df_curve_gauge_registry = local_df_curve_gauge_registry,
        df_bounty_formatted = local_df_bounty_formatetd,
        # df_current = df_current_bounties,
        # df_prior = df_prior_bounties,
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
        # graphJSON3 = graphJSON3,
        # graphJSON4 = graphJSON4


    )