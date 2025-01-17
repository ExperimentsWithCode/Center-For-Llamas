from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for
# from flask_login import current_user, login_required

from flask import Response
from flask import request

from datetime import datetime
import json
import plotly
import plotly.express as px



# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# from matplotlib.figure import Figure
# import io


# from .forms import AMMForm
from .models import  df_vote_aggregates, df_vote_choice
# from ..utility.api import get_proposals, get_proposal
# from ..address.routes import new_address
# from ..choice.routes import new_choice_list


# Blueprint Configuration
convex_snapshot_bp = Blueprint(
    'convex_snapshot_bp', __name__,
    url_prefix='/convex/snapshot',
    template_folder='templates',
    static_folder='static'
)

# proposal_end	proposal_title	choice	sum	count

@convex_snapshot_bp.route('/', methods=['GET'])
# @login_required
def index():
    # now = datetime.now()

    # Filter Data

    # local_df_gauge_votes = df_all_by_gauge.groupby(['voter', 'gauge_addr'], as_index=False).last()

    # Build chart
    fig = px.bar(df_vote_aggregates,
                    x=df_vote_aggregates['proposal_end'],
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
        'index_snapshot.jinja2',
        title='Convex Snapshot Gauge Weight Votes',
        template='snapshot-vote-index',
        body="",
        sum_current_votes = df_current_votes.total_vote_power.sum(),
        sum_prior_votes = df_prior_votes.total_vote_power.sum(),
        convex_snapshot_aggregate_votes = df_vote_aggregates,
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
        graphJSON3 = graphJSON3

    )


@convex_snapshot_bp.route('/show/<string:choice>', methods=['GET'])
# @login_required
def show(choice):
    # Filter Data
    # local_df_gauge_votes = df_gauge_votes_formatted.groupby(['voter', 'gauge_addr'], as_index=False).last()
    # local_df_gauge_votes = local_df_gauge_votes[local_df_gauge_votes['user'] == user]
    # local_df_gauge_votes = local_df_gauge_votes[local_df_gauge_votes['weight'] > 0]
    # local_df_gauge_votes = local_df_gauge_votes.sort_values("time", axis = 0, ascending = False)
    local_df_vote_choice = df_vote_choice[df_vote_choice['choice'] == choice]
    local_df_vote_choice = local_df_vote_choice.sort_values(["proposal_end", 'choice_power'], axis = 0, ascending = False)

    max_value = local_df_vote_choice['proposal_end'].max()
    df_current_votes = local_df_vote_choice[local_df_vote_choice['proposal_end'] == max_value]
    
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
                    x=local_df_vote_choice['proposal_end'],
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
                    x=local_df_vote_choice['proposal_end'],
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
        'show_snapshot.jinja2',
        title='Convex Snapshot Gauge Weight Votes',
        template='gauge-votes-show',
        body="",
        df_snapshot_user = local_df_vote_choice,
        current_votes = df_current_votes.choice_power.sum(),
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
        graphJSON3 = graphJSON3,
        graphJSON4 = graphJSON4,
    )