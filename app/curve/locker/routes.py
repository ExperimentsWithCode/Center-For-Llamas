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



# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# from matplotlib.figure import Figure
# import io


# from .forms import AMMForm
from .models import  df_history_data, df_current_locks, df_known_locks, df_locker_supply, get_lock_diffs
# from ..utility.api import get_proposals, get_proposal
# from ..address.routes import new_address
# from ..choice.routes import new_choice_list


# Blueprint Configuration
locker_bp = Blueprint(
    'locker_bp', __name__,
    url_prefix='/curve/locker',
    template_folder='templates',
    static_folder='static'
)

@locker_bp.route('/', methods=['GET'])
# @login_required
def index():

    # Build chart
    fig = px.bar(df_current_locks,
                    x=df_current_locks['final_lock_time'],
                    y=df_current_locks['balance_adj'],
                    # color='provider',
                    title='Final Lock Time by week',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    filtered_history = df_history_data[df_history_data['known_as'] != '_']
    fig = px.line(filtered_history,
                    x=filtered_history['timestamp'],
                    y=filtered_history['balance_adj'],
                    color='known_as',
                    line_shape='hv',
                    title='Cumulative Lock Comparison',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.pie(df_known_locks,
                    names=df_known_locks['known_as'],
                    values=df_known_locks['balance_adj'],
                    # color='provider',
                    title='Relative Lock weight',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    # hover_data=['symbol'], 
                    # labels={'symbol':'symbol'}
                    )
    fig.update_traces(textposition='inside', textinfo='percent+label')  # percent+label
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')


    # Build Plotly object
    graphJSON3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.line(df_locker_supply,
                    x=df_locker_supply['period_end_date'],
                    y=df_locker_supply['supply_difference_adj'],
                    # color='provider',
                    title='CRV Locked',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')
    # Build Plotly object
    graphJSON4 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        'index_locker.jinja2',
        title='Curve Locker',
        template='locker-index',
        body="",
        lockers = df_current_locks,
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
        graphJSON3 = graphJSON3,
        graphJSON4 = graphJSON4,

        
    )


@locker_bp.route('/show/<string:provider>', methods=['GET'])
# @login_required
def show(provider):
    now = datetime.now()
    provider = provider.lower()
    # Filter Data
    df_current_locks = df_history_data[df_history_data['provider'] == provider]
    # df_current_locks = df_history_data.groupby('provider', as_index=False).last()
    df_current_locks = df_current_locks.sort_values("timestamp", axis = 0, ascending = False)
    # Build chart
    fig = px.line(df_current_locks,
                    x=df_current_locks['timestamp'],
                    y=df_current_locks['balance_adj'],
                    # color='provider',
                    line_shape='hv',
                    title='Cumulative Lock',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Calc remaining lock
    final_lock_time = df_current_locks.iloc[0]['final_lock_time']
    diff_lock_weeks, diff_max_weeks = get_lock_diffs(final_lock_time)

    fig = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = diff_lock_weeks,
        mode = "gauge+number+delta",
        title = {'text': "Lock Efficiency (Weeks)"},
        delta = {'reference': diff_max_weeks},
        gauge = {'axis': {'range': [0, 225]},
                'steps' : [
                    {'range': [0, 52], 'color': "lightgray"},
                    {'range': [53, 104], 'color': "gray"},
                    {'range': [105, 156], 'color': "lightgray"},
                    {'range': [156, 208], 'color': "gray"},
                    {'range': [208, 225], 'color': "black"}],

                'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': diff_max_weeks}}))
    
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # Build Plotly object
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        'show_locker.jinja2',
        title='Curve Locker',
        template='locker-show',
        body="",
        lockers = df_current_locks,
        provider = provider,
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2
    )

# # """Logged-in page routes."""
# @locker_bp.route('/show/<string:proposal_id>', methods=['GET'])
# # @login_required
# def show(proposal_id):
#     proposal = Proposal.query.filter(Proposal.id==proposal_id).first()
#     return render_template(
#         'show_proposal.jinja2',
#         title=proposal.title,
#         template='proposal-show',
#         body="",
#         proposal = proposal
#     )

# # """Logged-in page routes."""
# @locker_bp.route('/<string:space_id>', methods=['GET'])
# # @login_required
# def indexspace(space_id):
#     proposals = Proposal.query.filter(Proposal.space_id==space_id).all()
#     return render_template(
#         'index_locker.jinja2',
#         title=space_id,
#         template='proposal-show',
#         body="",
#         proposals = proposals,
#         space_id = space_id
#     )

# # """Logged-in page routes."""
# @locker_bp.route('/load/<int:first>/<string:space_id>', methods=['GET'])
# # @login_required
# def load(first, space_id):
#     existing_proposals = Proposal.query.filter(Proposal.space_id == space_id).all()
#     if not existing_proposals:
#         print("NONE FOUND!!!!")
#         existing_proposals = []
#     else:
#         print(len(existing_proposals))
#     # first = 100
#     # existing_proposals = []
#     new_proposals = get_proposals(space_id, first, len(existing_proposals))
#     if len(new_proposals) > 0:
#         for p in new_proposals:
#             previous_entry = Proposal.query.filter(Proposal.id == p['id']).first()
#             author = new_address(p['author'])
#             if not previous_entry:
#                 new_proposal = Proposal(
#                     id = p['id'],
#                     title = p['title'],
#                     body = p['body'],
#                     start = p['start'],
#                     end = p['end'],
#                     snapshot = p['snapshot'],
#                     state = p['state'],
#                     author_address = author.address,
#                     space_id = p['space']['id'],
#                 )
#                 db.session.add(new_proposal)
#                 new_proposal.choices = new_choice_list(p['choices'], new_proposal.id)
#             else:
#                 print(p['title'])
#                 previous_entry.id = p['id'],
#                 previous_entry.title = p['title'],
#                 previous_entry.body = p['body'],
#                 previous_entry.start = p['start'],
#                 previous_entry.end = p['end'],
#                 previous_entry.snapshot = p['snapshot'],
#                 previous_entry.state = p['state'],
#                 previous_entry.author_address = author.address,
#                 previous_entry.space_id = p['space']['id'],
#                 previous_entry.author = new_address(p['author'])
#                 previous_entry.choices = new_choice_list(p['choices'], previous_entry.id)
#         db.session.commit()
#     return redirect(url_for('locker_bp.indexspace', space_id=space_id))

# # """Logged-in page routes."""
# @locker_bp.route('/reload/<string:proposal_id>', methods=['GET'])
# # @login_required
# def reload(proposal_id):
#     existing_proposal = Proposal.query.filter(Proposal.id == proposal_id).first()
#     refreshed_proposal = get_proposal(proposal_id)
#     if existing_proposal:
#         print(existing_proposal.title)
#         author = new_address(refreshed_proposal['author'])
#         existing_proposal.title = refreshed_proposal['title'],
#         existing_proposal.body = refreshed_proposal['body'],
#         existing_proposal.start = refreshed_proposal['start'],
#         existing_proposal.end = refreshed_proposal['end'],
#         existing_proposal.snapshot = refreshed_proposal['snapshot'],
#         existing_proposal.state = refreshed_proposal['state'],
#         existing_proposal.author_address = author.address,
#         existing_proposal.space_id = refreshed_proposal['space']['id'],
#         db.session.add(existing_proposal)
#         existing_proposal.choices = new_choice_list(refreshed_proposal['choices'], existing_proposal.id)

#         db.session.add(existing_proposal)
#         db.session.commit()
#     return redirect(url_for('locker_bp.show', proposal_id=proposal_id))


# def get_proposal(proposal_id):
#     return Proposal.query.filter(Proposal.id == proposal_id).first()
