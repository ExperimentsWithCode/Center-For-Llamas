from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for
# from flask_login import current_user, login_required

from flask import Response
from flask import request

from datetime import datetime
import json
import plotly
import plotly.express as px

from .models import df_bounty_formatted

# Blueprint Configuration
votium_bounties_bp = Blueprint(
    'votium_bounties_bp', __name__,
    url_prefix='/curve/gauges',
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
                    x=df_bounty_formatted['period_end_date'],
                    y=df_bounty_formatted['total_vote_power'],
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
    # current_period = periods[-1]
    # prior_period = periods[-2]
    # df_current_votes = df_meta_gauge_aggregate[df_meta_gauge_aggregate['this_period'] == current_period]
    # df_prior_votes = df_meta_gauge_aggregate[df_meta_gauge_aggregate['this_period'] == prior_period]

    # # Build chart
    fig = px.bar(df_bounty_formatted,
                    x=df_bounty_formatted['period_end_date'],
                    y=df_bounty_formatted['votes_per_dollar'],
                    color='gauge_ref',
                    title='Votes Per Dollar Bounties',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )

    # # Build Plotly object
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)



    periods = df_bounty_formatted.period.unique()
    periods.sort()
    current_period = periods[-1]
    prior_period = periods[-2]
    df_current_bounties = df_bounty_formatted[df_bounty_formatted['period'] == current_period]
    df_prior_bounties = df_bounty_formatted[df_bounty_formatted['period'] == prior_period]


    # # Build chart
    fig = px.pie(df_current_bounties, 
                values=df_current_bounties['votes_per_dollar'],
                names=df_current_bounties['gauge_ref'],
                title=f"Prior Round Vote Distribution {current_period}",
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
                title=f"Prior Round Vote Distribution {prior_period}",
                # hover_data=['gauge_addr'], labels={'gauge_addr':'gauge_addr'}
                )
    fig.update_traces(textposition='inside', textinfo='percent')  # percent+label
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # # Build Plotly object
    graphJSON4 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

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
        graphJSON4 = graphJSON4


    )
