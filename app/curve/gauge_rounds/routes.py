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
from .models import  df_all_by_user, df_all_by_gauge, df_meta_gauge_aggregate
# from ..utility.api import get_proposals, get_proposal
# from ..address.routes import new_address
# from ..choice.routes import new_choice_list




# Blueprint Configuration
gauge_rounds_bp = Blueprint(
    'gauge_rounds_bp', __name__,
    url_prefix='/curve/gauge_rounds',
    template_folder='templates',
    static_folder='static'
)

@gauge_rounds_bp.route('/', methods=['GET'])
# @login_required
def index():
    now = datetime.now()

    # Filter Data

    # local_df_gauge_votes = df_all_by_gauge.groupby(['voter', 'gauge_addr'], as_index=False).last()

    # Build chart
    fig = px.bar(df_meta_gauge_aggregate,
                    x=df_meta_gauge_aggregate['period_end_date'],
                    y=df_meta_gauge_aggregate['total_vote_power'],
                    color='gauge_addr',
                    title='Gauge Round Vote Weights',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    periods = df_meta_gauge_aggregate.this_period.unique()
    periods.sort()
    current_period = periods[-1]
    prior_period = periods[-2]
    df_current_votes = df_meta_gauge_aggregate[df_meta_gauge_aggregate['this_period'] == current_period]
    df_prior_votes = df_meta_gauge_aggregate[df_meta_gauge_aggregate['this_period'] == prior_period]

    # # Build chart
    fig = px.pie(df_current_votes, 
                values=df_current_votes['total_vote_power'],
                names=df_current_votes['gauge_addr'],
                title=f"Current Round Vote Distribution {current_period}",
                hover_data=['symbol'], labels={'symbol':'symbol'}
                )
    fig.update_traces(textposition='inside', textinfo='percent')  # percent+label
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # # Build Plotly object
    graphJSON3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # # Build chart
    fig = px.pie(df_prior_votes, 
                values=df_prior_votes['total_vote_power'],
                names=df_prior_votes['gauge_addr'],
                title=f"Prior Round Vote Distribution {prior_period}",
                hover_data=['symbol'], labels={'symbol':'symbol'}
                )
    fig.update_traces(textposition='inside', textinfo='percent')  # percent+label
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # # Build Plotly object
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        'index_meta_aggregate_votes.jinja2',
        title='Curve Gauge Rounds',
        template='gauge-round-index',
        body="",
        meta_gauge_aggregate_votes = df_meta_gauge_aggregate,
        sum_current_votes = df_current_votes.total_vote_power.sum(),
        sum_prior_votes = df_prior_votes.total_vote_power.sum(),
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
        graphJSON3 = graphJSON3

    )


@gauge_rounds_bp.route('/show/<string:gauge_addr>', methods=['GET'])
# @login_required
def show(gauge_addr):
    df_curve_gauge_registry = app.config['df_curve_gauge_registry']
    local_df_curve_gauge_registry = df_curve_gauge_registry[df_curve_gauge_registry['gauge_addr'] == gauge_addr]

    # Filter Data
    # local_df_gauge_votes = df_gauge_votes_formatted.groupby(['voter', 'gauge_addr'], as_index=False).last()
    # local_df_gauge_votes = local_df_gauge_votes[local_df_gauge_votes['user'] == user]
    # local_df_gauge_votes = local_df_gauge_votes[local_df_gauge_votes['weight'] > 0]
    # local_df_gauge_votes = local_df_gauge_votes.sort_values("time", axis = 0, ascending = False)
    local_df_gauge_rounds = df_all_by_user[df_all_by_user['gauge_addr'] == gauge_addr]
    local_df_gauge_rounds = local_df_gauge_rounds.sort_values(["this_period", 'vote_power'], axis = 0, ascending = False)

    max_value = local_df_gauge_rounds['this_period'].max()
    df_current_votes = local_df_gauge_rounds[local_df_gauge_rounds['this_period'] == max_value]
    
    # # Build chart
    fig = px.pie(df_current_votes, 
                values=df_current_votes['vote_power'],
                names=df_current_votes['user'],
                title='Current Round Voter Distribution',
                hover_data=['known_as_x'], labels={'known_as_x':'known_as'}
                )
    fig.update_traces(textposition='inside', textinfo='percent')  # percent+label
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        # # Build chart
    fig = px.bar(local_df_gauge_rounds,
                    x=local_df_gauge_rounds['period_end_date'],
                    y=local_df_gauge_rounds['vote_power'],
                    color='user',
                    title='Votes Per Round',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # # Build Plotly object
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        # # Build chart
    fig = px.bar(local_df_gauge_rounds,
                    x=local_df_gauge_rounds['period_end_date'],
                    y=local_df_gauge_rounds['vote_power'],
                    color='known_as_x',
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
                values=df_current_votes['vote_power'],
                names=df_current_votes['known_as_x'],
                title='Current Round Voter Distribution',
                hover_data=['known_as_x'], labels={'known_as_x':'known_as'}
                )
    fig.update_traces(textposition='inside', textinfo='percent')  # percent+label
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # # Build Plotly object
    graphJSON4 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template(
        'show_gauge_rounds.jinja2',
        title='Curve Gauge Rounds',
        template='gauge-votes-show',
        body="",
        local_df_curve_gauge_registry = local_df_curve_gauge_registry,
        df_gauge_round_by_user = local_df_gauge_rounds,
        current_votes = df_current_votes.vote_power.sum(),
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
        graphJSON3 = graphJSON3,
        graphJSON4 = graphJSON4,



    )