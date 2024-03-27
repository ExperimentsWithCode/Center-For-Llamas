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
from .models import  df_checkpoints, df_checkpoints_agg
# from ..utility.api import get_proposals, get_proposal
# from ..address.routes import new_address
# from ..choice.routes import new_choice_list

try:
    # curve_gauge_registry = app.config['df_curve_gauge_registry']
    gauge_registry = app.config['gauge_registry']
except: 
    # from app.curve.gauges import df_curve_gauge_registry as curve_gauge_registry
    from app.curve.gauges.models import gauge_registry



# Blueprint Configuration
gauge_rounds_bp = Blueprint(
    'gauge_rounds_bp', __name__,
    url_prefix='/curve/gauge_rounds',
    template_folder='templates',
    static_folder='static'
)

def get_checkpoint_info(df):
    return {
        'current': {
            'id': df.checkpoint_id.unique()[-1],
            'timestamp': df.checkpoint_timestamp.unique()[-1]
        },
        'prior': {
            'id': df.checkpoint_id.unique()[-2],
            'timestamp': df.checkpoint_timestamp.unique()[-2]
        },
        }


@gauge_rounds_bp.route('/', methods=['GET'])
# @login_required
def index():
    now = datetime.now()

    # Filter Data
    local_df_checkpoints_agg = df_checkpoints_agg.sort_values(['checkpoint_id', 'total_vote_power'], ascending=False)
    # local_df_gauge_votes = df_checkpoints_agg.groupby(['voter', 'gauge_addr'], as_index=False).last()
    checkpoint_timestamps = local_df_checkpoints_agg.checkpoint_timestamp.unique()
    checkpoint_timestamps = sorted(checkpoint_timestamps)

    current_checkpoint = local_df_checkpoints_agg.checkpoint_id.max()
    prior_checkpoint = current_checkpoint - 1
    df_current_votes = local_df_checkpoints_agg[local_df_checkpoints_agg['checkpoint_id'] == current_checkpoint]
    df_prior_votes = local_df_checkpoints_agg[local_df_checkpoints_agg['checkpoint_id'] == prior_checkpoint]


    # Build chart
    fig = px.bar(local_df_checkpoints_agg,
                    x=local_df_checkpoints_agg['checkpoint_timestamp'],
                    y=local_df_checkpoints_agg['total_vote_power'],
                    color='gauge_symbol',
                    title='Gauge Round Vote Weights',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)



    # # Build chart
    fig = px.pie(df_current_votes, 
                values=df_current_votes['total_vote_power'],
                names=df_current_votes['gauge_symbol'],
                title=f"Current Round Vote Distribution {current_checkpoint}",
                hover_data=['gauge_addr'], labels={'gauge_addr':'gauge_addr'}
                )
    fig.update_traces(textposition='inside', textinfo='percent')  # percent+label
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # # Build Plotly object
    graphJSON3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # # Build chart
    fig = px.pie(df_prior_votes, 
                values=df_prior_votes['total_vote_power'],
                names=df_prior_votes['gauge_symbol'],
                title=f"Prior Round Vote Distribution {prior_checkpoint}",
                hover_data=['gauge_addr'], labels={'gauge_addr':'gauge_addr'}
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
        meta_gauge_aggregate_votes = local_df_checkpoints_agg,
        sum_current_votes = df_current_votes.total_vote_power.sum(),
        sum_prior_votes = df_prior_votes.total_vote_power.sum(),
        checkpoint_info = get_checkpoint_info(df_checkpoints_agg),
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
    local_df_gauge_rounds = df_checkpoints[df_checkpoints['gauge_addr'] == gauge_addr]
    local_df_gauge_rounds = local_df_gauge_rounds.sort_values(["checkpoint_id", 'vote_power'], axis = 0, ascending = False)

    if len(local_df_gauge_rounds) == 0:
        return render_template(
            'gauge_rounds_not_found.jinja2',
            title='Votes Per Gauge Round',
            template='gauge-votes-show',
            body="",
            local_df_curve_gauge_registry = local_df_curve_gauge_registry,
            )
    
    checkpoint_timestamps = df_checkpoints_agg.checkpoint_timestamp.unique()
    checkpoint_timestamps = sorted(checkpoint_timestamps)
    if len(checkpoint_timestamps) >= 2:
        current_period = checkpoint_timestamps[-1]
        prior_period = checkpoint_timestamps[-2]
    elif len(checkpoint_timestamps == 1):
        current_period = checkpoint_timestamps[-1]
        prior_period = None

    df_current_votes = local_df_gauge_rounds[local_df_gauge_rounds['checkpoint_timestamp'] == current_period]
    if prior_period:
        df_prior_votes = local_df_gauge_rounds[local_df_gauge_rounds['checkpoint_timestamp'] == prior_period]
    else:
        df_prior_votes == []

    # df_current_votes = local_df_gauge_rounds[local_df_gauge_rounds['checkpoint_timestamp'] == max_value]
    
    # # Build chart
    fig = px.pie(df_current_votes, 
                values=df_current_votes['vote_power'],
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
    fig = px.bar(local_df_gauge_rounds,
                    x=local_df_gauge_rounds['checkpoint_timestamp'],
                    y=local_df_gauge_rounds['vote_power'],
                    color='voter',
                    title='Votes Per Gauge Round',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # # Build Plotly object
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        # # Build chart
    fig = px.bar(local_df_gauge_rounds,
                    x=local_df_gauge_rounds['checkpoint_timestamp'],
                    y=local_df_gauge_rounds['vote_power'],
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
                values=df_current_votes['vote_power'],
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
        'show_gauge_rounds.jinja2',
        title='Curve Gauge Rounds',
        template='gauge-votes-show',
        body="",
        local_df_curve_gauge_registry = local_df_curve_gauge_registry,
        local_df_gauge_rounds = local_df_gauge_rounds,
        sum_current_votes = df_current_votes.vote_power.sum() if len(df_current_votes) > 0 else 0,
        sum_prior_votes = df_prior_votes.vote_power.sum() if len(df_prior_votes) > 0 else 0,
        checkpoint_info = get_checkpoint_info(df_checkpoints_agg),
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
        graphJSON3 = graphJSON3,
        graphJSON4 = graphJSON4,
        pool_shorthand = gauge_registry.get_shorthand_pool(gauge_addr)
    )