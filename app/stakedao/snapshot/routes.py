from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for
# from flask_login import current_user, login_required

from flask import Response
from flask import request

from datetime import datetime
import json
import plotly
import plotly.express as px

from .models import df_stakedao_snapshot_vote_aggregates



# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# from matplotlib.figure import Figure
# import io


# from .forms import AMMForm
# from .models import  df_stakedao_snapshot_vote_aggregates as  df_vote_aggregates 
# from .models import  df_stakedao_snapshot_vote_choice as df_vote_choice
# from ..utility.api import get_proposals, get_proposal
# from ..address.routes import new_address
# from ..choice.routes import new_choice_list


# Blueprint Configuration
stakedao_snapshot_bp = Blueprint(
    'stakedao_snapshot_bp', __name__,
    url_prefix='/stakedao/snapshot',
    template_folder='templates',
    static_folder='static'
)

try:
    # curve_gauge_registry = app.config['df_curve_gauge_registry']
    df_curve_gauge_registry = app.config['df_curve_gauge_registry']
except: 
    # from app.curve.gauges import df_curve_gauge_registry as curve_gauge_registry
    from app.curve.gauges.models import df_curve_gauge_registry

# df_vote_aggregates = app.config['df_stakedao_snapshot_vote_aggregates']
# df_vote_choice = app.config['df_stakedao_snapshot_vote_choice']


# proposal_end	proposal_title	choice	sum	count

@stakedao_snapshot_bp.route('/', methods=['GET'])
# @login_required
def index():
    df_vote_aggregates = app.config['df_stakedao_snapshot_vote_aggregates']

    # Filter Data

    # local_df_gauge_votes = df_all_by_gauge.groupby(['voter', 'gauge_addr'], as_index=False).last()

    # Build chart
    fig = px.bar(df_vote_aggregates,
                    x=df_vote_aggregates['period_end_date'],
                    y=df_vote_aggregates['total_vote_power'],
                    color='choice',
                    title='Gauge Weight Round Vote Weights',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    periods = df_vote_aggregates.proposal_end.unique()
    periods.sort()
    current_period = periods[-1]
    prior_period = periods[-2]
    df_current_votes = df_vote_aggregates[df_vote_aggregates['proposal_end'] == current_period]
    df_prior_votes = df_vote_aggregates[df_vote_aggregates['proposal_end'] == prior_period]

    # # Build chart
    fig = px.pie(df_current_votes, 
                values=df_current_votes['total_vote_power'],
                names=df_current_votes['choice'],
                title=f"Current Round Vote Distribution {current_period}",
                # hover_data=['symbol'], labels={'symbol':'symbol'}
                )
    fig.update_traces(textposition='inside', textinfo='percent')  # percent+label
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # # Build Plotly object
    graphJSON3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # # Build chart
    fig = px.pie(df_prior_votes, 
                values=df_prior_votes['total_vote_power'],
                names=df_prior_votes['choice'],
                title=f"Prior Round Vote Distribution {prior_period}",
                # hover_data=['symbol'], labels={'symbol':'symbol'}
                )
    fig.update_traces(textposition='inside', textinfo='percent')  # percent+label
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # # Build Plotly object
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        'index_stakedao_snapshot.jinja2',
        title='Stakedao Snapshot Gauge Weight Votes',
        template='snapshot-vote-index',
        body="",
        sum_current_votes = df_current_votes.total_vote_power.sum(),
        sum_prior_votes = df_prior_votes.total_vote_power.sum(),
        stakedao_snapshot_aggregate_votes = df_vote_aggregates,
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
        graphJSON3 = graphJSON3

    )


@stakedao_snapshot_bp.route('/show/<string:choice>', methods=['GET'])
# @login_required
def show(choice):
    df_vote_choice = app.config['df_stakedao_snapshot_vote_choice']

    if choice[:2] == "0x":
        local_df_vote_choice = df_vote_choice[df_vote_choice['gauge_addr'] == choice]
        gauge_addr = choice
    else:
        local_df_vote_choice = df_vote_choice[df_vote_choice['choice'] == choice]
        gauge_addr = None
        if len(local_df_vote_choice)> 0:
            gauge_addr = local_df_vote_choice.iloc[0]['gauge_addr']

    if len(local_df_vote_choice) == 0:
        return render_template(
            'stakedao_not_found.jinja2',
            title='Stakedao Snapshot Gauge Weight Votes',
            template='gauge-votes-show',
            body="",
            gauge_addr = gauge_addr,
            choice = choice
        )
    
    local_df_curve_gauge_registry = df_curve_gauge_registry[df_curve_gauge_registry['gauge_addr'] == gauge_addr ]

    local_df_vote_choice = local_df_vote_choice.sort_values(["proposal_end", 'choice_power'], axis = 0, ascending = False)

    proposal_end_dates = df_vote_choice.proposal_end.unique()
    proposal_end_dates = sorted(proposal_end_dates)
    current = proposal_end_dates[-1]
    prior = proposal_end_dates[-2]

    df_current_votes = local_df_vote_choice[local_df_vote_choice['proposal_end'] == current]
    df_prior_votes = local_df_vote_choice[local_df_vote_choice['proposal_end'] == prior]


    # # Build chart
    fig = px.pie(df_current_votes, 
                values=df_current_votes['choice_power'],
                names=df_current_votes['voter'],
                title='Current Round Voter Distribution',
                hover_data=['known_as'], labels={'known_as':'known_as'}
                )
    fig.update_traces(textposition='inside', textinfo='percent')  # percent+label
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        # # Build chart
    fig = px.bar(local_df_vote_choice,
                    x=local_df_vote_choice['period_end_date'],
                    y=local_df_vote_choice['choice_power'],
                    color='voter',
                    title='Votes Per Round',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # # Build Plotly object
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        # # Build chart
    fig = px.bar(local_df_vote_choice,
                    x=local_df_vote_choice['period_end_date'],
                    y=local_df_vote_choice['choice_power'],
                    color='known_as',
                    title='Votes Per Round',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # # Build Plotly object
    graphJSON3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        # # Build chart
    fig = px.pie(df_current_votes, 
                values=df_current_votes['choice_power'],
                names=df_current_votes['known_as'],
                title='Current Round Voter Distribution',
                hover_data=['known_as'], labels={'known_as':'known_as'}
                )
    fig.update_traces(textposition='inside', textinfo='percent')  # percent+label
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # # Build Plotly object
    graphJSON4 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template(
        'show_stakedao_snapshot.jinja2',
        title='Stakedao Snapshot Gauge Weight Votes',
        template='gauge-votes-show',
        body="",
        df_snapshot_user = local_df_vote_choice,

        current_votes = df_current_votes.choice_power.sum(),
        prior_votes = df_prior_votes.choice_power.sum(),
        local_df_curve_gauge_registry = local_df_curve_gauge_registry,

        # votium_bounty_registry = app.config['votium_bounty_registry'],
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
        graphJSON3 = graphJSON3,
        graphJSON4 = graphJSON4,
    )



@stakedao_snapshot_bp.route('/voter/<string:voter>', methods=['GET'])
def voter(voter):
    df_vote_choice = app.config['df_stakedao_snapshot_vote_choice']

    # Filter Data
    # local_df_gauge_votes = df_gauge_votes_formatted.groupby(['voter', 'gauge_addr'], as_index=False).last()
    # local_df_gauge_votes = local_df_gauge_votes[local_df_gauge_votes['user'] == user]
    # local_df_gauge_votes = local_df_gauge_votes[local_df_gauge_votes['weight'] > 0]
    # local_df_gauge_votes = local_df_gauge_votes.sort_values("time", axis = 0, ascending = False)

    local_df_vote_choice = df_vote_choice[df_vote_choice['voter'] == voter]
        
    local_df_vote_choice = local_df_vote_choice.sort_values(["proposal_end", 'choice_power'], axis = 0, ascending = False)

    max_value = local_df_vote_choice['proposal_end'].max()
    df_current_votes = local_df_vote_choice[local_df_vote_choice['proposal_end'] == max_value]
    
    # # Build chart
    fig = px.pie(df_current_votes, 
                values=df_current_votes['choice_power'],
                names=df_current_votes['choice'],
                title='Current Round Gauge Distribution',
                # hover_data=['known_as'], labels={'known_as':'known_as'}
                )
    fig.update_traces(textposition='inside', textinfo='percent')  # percent+label
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        # # Build chart
    fig = px.bar(local_df_vote_choice,
                    x=local_df_vote_choice['proposal_end'],
                    y=local_df_vote_choice['choice_power'],
                    color='choice',
                    title='Choices Per Round',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # # Build Plotly object
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    #     # # Build chart
    # fig = px.bar(local_df_vote_choice,
    #                 x=local_df_vote_choice['proposal_end'],
    #                 y=local_df_vote_choice['choice_power'],
    #                 color='choice',
    #                 title='Votes Per Round',
    #                 # facet_row=facet_row,
    #                 # facet_col_wrap=facet_col_wrap
    #                 )
    #     # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    # fig.update_layout(autotypenumbers='convert types')

    # # # Build Plotly object
    # graphJSON3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # # Build chart
    fig = px.line(local_df_vote_choice,
                    x=local_df_vote_choice['period_end_date'],
                    y=local_df_vote_choice['available_power'],
                    # color='choice',
                    title='sdCRV Held',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # # Build Plotly object
    graphJSON3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template(
        'show_stakedao_voter_snapshot.jinja2',
        title='StakeDAO Snapshot Voter Profile',
        template='snapshot-voter-show',
        body="",
        df_snapshot_user = local_df_vote_choice,
        current_votes = df_current_votes.choice_power.sum(),
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
        graphJSON3 = graphJSON3
        # graphJSON4 = graphJSON4,
    )