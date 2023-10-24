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
from .models import  df_gauge_votes_formatted, df_current_gauge_votes
# from ..utility.api import get_proposals, get_proposal
# from ..address.routes import new_address
# from ..choice.routes import new_choice_list


# Blueprint Configuration
gauge_votes_bp = Blueprint(
    'gauge_votes_bp', __name__,
    url_prefix='/curve/gauge_votes',
    template_folder='templates',
    static_folder='static'
)

@gauge_votes_bp.route('/', methods=['GET'])
# @login_required
def index():
    now = datetime.now()
    df_current_gauge_votes
    # Filter Data
    local_df_gauge_votes = df_current_gauge_votes[[
            'period_end_date','period', 'voter',
            ]].groupby([
                'period_end_date', 'period', 
            ])['voter'].agg(['count']).reset_index()

 
    # Build chart
    fig = px.line(local_df_gauge_votes,
                    x=local_df_gauge_votes['period_end_date'],
                    y=local_df_gauge_votes['count'],
                    # color='known_as',
                    title='# of Votes per round',
                    line_shape='hv',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    hover_data=['period'], labels={'period':'period'}

                    )

    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        'index_gauge_votes.jinja2',
        title='Curve Gauge Votes',
        template='gauge-vote-index',
        body="",
        votes = df_current_gauge_votes,
        graphJSON = graphJSON,
    )


@gauge_votes_bp.route('/show/<string:user>', methods=['GET'])
# @login_required
def show(user):
    now = datetime.now()
    user = user.lower()
    # Filter Data
    if not (df_gauge_votes_formatted['user'] == user).any():
        return render_template(
            'gauge_votes_not_found.jinja2',
            title='Curve Gauge Votes',
            template='gauge-votes-show',
            body="",
            user = user,
            )
    local_df_gauge_votes = df_gauge_votes_formatted.groupby(['voter', 'gauge_addr'], as_index=False).last()
    local_df_gauge_votes = local_df_gauge_votes[local_df_gauge_votes['user'] == user]

    local_df_gauge_votes = local_df_gauge_votes.sort_values("time", axis = 0, ascending = False)
    local_df_gauge_votes_inactive = local_df_gauge_votes[local_df_gauge_votes['weight'] == 0]
    local_df_gauge_votes = local_df_gauge_votes[local_df_gauge_votes['weight'] > 0]

    # # Build chart
    fig = px.pie(local_df_gauge_votes, 
                values=local_df_gauge_votes['weight'],
                names=local_df_gauge_votes['gauge_addr'],
                title='Vote Distribution',
                hover_data=['symbol'], labels={'symbol':'symbol'}
                )
    fig.update_traces(textposition='inside', textinfo='percent')  # percent+label
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    # fig.update_layout(autotypenumbers='convert types')

    # # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        'show_gauge_votes.jinja2',
        title='Curve Gauge Votes',
        template='gauge-votes-show',
        body="",
        votes = local_df_gauge_votes,
        inactive_votes = local_df_gauge_votes_inactive,
        user = user,
        graphJSON = graphJSON
    )



# @gauge_votes_bp.route('/', methods=['GET'])
# # @login_required
# def index():


#     local_df_gauge_votes = df_gauge_votes_formatted.sort_values("time", axis = 0, ascending = False)
#     local_df_gauge_votes_inactive = df_gauge_votes_formatted[df_gauge_votes_formatted['weight'] == 0]
#     local_df_gauge_votes = df_gauge_votes_formatted[df_gauge_votes_formatted['weight'] > 0]    # Filter Data

#     local_df_gauge_votes_count = local_df_gauge_votes[[
#         'period_end_date','period', 'voter',
#             'period_end_date', 'period', 'voter', 
#         ])['time'].agg(['count']).reset_index()
    
#     local_df_gauge_votes.value_counts()

#     fig = make_subplots(specs=[[{"secondary_y": True}]])
#     # fig = go.Figure()
#     fig.update_layout(
#         title=f"Curve Votes",
#         # xaxis_title="X Axis Title",
#     #     yaxis_title="Y Axis Title",
#     #     legend_title="Legend Title",
#         font=dict(
#             family="Courier New, monospace",
#             size=18,
#             color="RebeccaPurple"
#         )
#     )


#     fig = fig.add_trace(
#         go.Scatter(
#             x = df.block_timestamp,
#             y = df.c_balance, 
#             name = "Collateral Token Balance",
#             mode='lines',
#             marker_color="green",
#         ),
#         secondary_y=False
#     )


#     fig = fig.add_trace(
#         go.Scatter(
#             x = df.block_timestamp,
#             y = df.d_balance, 
#             name = "Debt Token Balance",
#             mode='lines',
#             # marker_color="red"
#         ),
#         secondary_y=False
#     )

#     fig = fig.add_trace(
#         go.Scatter(
#             x=price_feed.block_timestamp,
#             y=price_feed.usd_price,
#             name="Curve Price (USD)",
#         ),
#         secondary_y=True

#     )






#     # local_df_gauge_voters = df_all_votes[[
#     #         'period_end_date','period', 'voter', 'time'
#     #         ]].groupby([
#     #             'period_end_date', 'period', 'voter', 
#     #         ])['time'].agg(['count']).reset_index()

#     # local_df_gauge_votes = df_current_gauge_votes[[
#     #         'period_end_date','period', 'time',
#     #         ]].groupby([
#     #             'period_end_date', 'period', 
#     #         ])['time'].agg(['count']).reset_index()
#     # Build chart
#     fig = px.line(local_df_gauge_voters,
#                     x=local_df_gauge_voters['period_end_date'],
#                     y=local_df_gauge_voters['count'],
#                     # color='known_as',
#                     title='# of Voters per round',
#                     line_shape='hv',
#                     # facet_row=facet_row,
#                     # facet_col_wrap=facet_col_wrap
#                     hover_data=['period'], labels={'period':'period'}

#                     )

#     fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
#     fig.update_layout(autotypenumbers='convert types')

#     # Build Plotly object
#     graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

#     # Build chart
#     fig = px.bar(local_df_gauge_votes,
#                     x=local_df_gauge_votes['period_end_date'],
#                     y=local_df_gauge_votes['count'],
#                     # color='known_as',
#                     title='# of Votes per round',
#                     line_shape='hv',
#                     # facet_row=facet_row,
#                     # facet_col_wrap=facet_col_wrap
#                     hover_data=['period'], labels={'period':'period'}

#                     )

#     fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
#     fig.update_layout(autotypenumbers='convert types')

#     # Build Plotly object
#     graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

#     return render_template(
#         'index_gauge_votes.jinja2',
#         title='Curve Gauge Votes',
#         template='gauge-vote-index',
#         body="",
#         votes = df_current_gauge_votes,
#         graphJSON = graphJSON,
#         graphJSON2 = graphJSON2,

#     )
