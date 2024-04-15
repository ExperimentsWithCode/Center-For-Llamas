from flask import current_app as app

from flask import Blueprint, render_template, redirect, url_for
# from flask_login import current_user, login_required

from flask import Response
from flask import request

from datetime import datetime as dt
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app.data.local_storage import pd


# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# from matplotlib.figure import Figure
# import io

from app.stakedao.delegations.models import df_stakedao_delegations

from app.utilities.utility import (
    format_plotly_figure,
    get_now,
    get_address_profile

)

# Blueprint Configuration
stakedao_snapshot_delegations_bp = Blueprint(
    'stakedao_snapshot_delegations_bp', __name__,
    url_prefix='/stakedao/delegations',
    template_folder='templates',
    static_folder='static'
)

# df_vote_aggregates = app.config['df_stakedao_snapshot_vote_aggregates']
# df_vote_choice = app.config['df_stakedao_snapshot_vote_choice']


# proposal_end	proposal_title	choice	sum	count

@stakedao_snapshot_delegations_bp.route('/', methods=['GET'])
# @login_required
def index():

    df_stakedao_delegations_agg = app.config['df_stakedao_delegations_agg']
    df_stakedao_delegations = app.config['df_stakedao_delegations']

    
    # Filter Data


    # Build chart
    temp_df_stakedao_delegations_agg = df_stakedao_delegations_agg.sort_values(['proposal_start', 'total_delegated'], ascending = False)
    fig = px.line(temp_df_stakedao_delegations_agg, x="proposal_start", y="total_delegated", color='delegate')
    fig.update_layout(
        title=f"Delegated Balance Per Delegate",
    #     xaxis_title="X Axis Title",
    #     yaxis_title="Y Axis Title",
    #     legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        ),
        # height= 1000,
    )
    fig = format_plotly_figure(fig)

    # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)



    temp_df_stakedao_delegations_agg = df_stakedao_delegations_agg.sort_values(['proposal_start', 'delegators_count'], ascending = False)
    fig = px.line(temp_df_stakedao_delegations_agg, x="proposal_start", y="delegators_count", color='delegate')
    fig.update_layout(
        title=f"Delegator Count Per Delegate",
    #     xaxis_title="X Axis Title",
    #     yaxis_title="Y Axis Title",
    #     legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        ),
        # height= 1000,
    )
    fig = format_plotly_figure(fig)

    # # Build Plotly object
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    
    return render_template(
        'index_stakedao_delegations.jinja2',
        title='stakedao Delegations',
        template='stakedao-delegations-index',
        body="",
        df_stakedao_delegations = df_stakedao_delegations,
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
    )



@stakedao_snapshot_delegations_bp.route('/delegate/<string:delegate>', methods=['GET'])
def delegate(delegate):
    # df_vote_choice = app.config['df_stakedao_snapshot_vote_choice']
    df_stakedao_delegation_locks_per_proposal = app.config['df_stakedao_delegation_locks_per_proposal']
    df_stakedao_delegations_agg = app.config['df_stakedao_delegations_agg']

    # Filter Data

    # Aggregate Delegate
    local_df_stakedao_delegate_agg = df_stakedao_delegations_agg[df_stakedao_delegations_agg['delegate'] == delegate]
    local_df_stakedao_delegate_agg = local_df_stakedao_delegate_agg.sort_values(["proposal_start", 'total_delegated'], axis = 0, ascending = False)


    local_df_stakedao_delegation_locks_per_proposal = df_stakedao_delegation_locks_per_proposal[
        df_stakedao_delegation_locks_per_proposal['delegate'] == delegate
        ]   
    local_df_stakedao_delegation_locks_per_proposal = local_df_stakedao_delegation_locks_per_proposal.sort_values(["proposal_start", 'staked_balance'], axis = 0, ascending = False)

    local_df_current_delegate_locks = local_df_stakedao_delegation_locks_per_proposal[
        local_df_stakedao_delegation_locks_per_proposal['proposal_start'] == local_df_stakedao_delegation_locks_per_proposal.proposal_start.max()
    ]

    local_delegations = local_df_stakedao_delegation_locks_per_proposal[
            ['delegator', 'delegator_known_as', 'proposal_start', 'proposal_title', 'staked_balance']
        ].groupby(['delegator']).head(1)
    
    graph_list = []
    # Build chart

    fig = px.bar(local_df_stakedao_delegate_agg,
                    x=local_df_stakedao_delegate_agg['proposal_start'],
                    y=local_df_stakedao_delegate_agg['total_delegated'],
                    color='delegators_count',
                    title='sdCRV Delegated Power by Delegate',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')
    fig = format_plotly_figure(fig)

    # # Build Plotly object
    graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))


    # # Build chart
    fig = px.pie(local_df_current_delegate_locks, 
                values=local_df_current_delegate_locks['staked_balance'],
                names=local_df_current_delegate_locks['delegator_known_as'],
                title='Current Round Gauge Distribution',
                # hover_data=['known_as'], labels={'known_as':'known_as'}
                )
    fig.update_traces(textposition='inside', textinfo='percent')
    fig = format_plotly_figure(fig)
 
    # # Build Plotly object
    graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

    # # Build chart
    fig = px.pie(local_df_current_delegate_locks, 
                values=local_df_current_delegate_locks['staked_balance'],
                names=local_df_current_delegate_locks['delegator'],
                title='Current Round Gauge Distribution',
                # hover_data=['known_as'], labels={'known_as':'known_as'}
                )
    fig.update_traces(textposition='inside', textinfo='percent') 
    fig = format_plotly_figure(fig)

    # # Build Plotly object
    graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))
    # # # Build chart
    # fig = px.bar(local_df_locker_user_epoch,
    #                 x=local_df_locker_user_epoch['proposal_start'],
    #                 y=local_df_locker_user_epoch['staked_balance'],
    #                 color='delegate',
    #                 title='Locked sdCRV by Delegate',
    #                 # facet_row=facet_row,
    #                 # facet_col_wrap=facet_col_wrap
    #                 )
    # fig.update_layout(autotypenumbers='convert types')
    # fig.update_yaxes(rangemode="tozero")
    # # # Build Plotly object
    # graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))



    return render_template(
        'show_stakedao_snapshot_delegate.jinja2',
        title='stakedao Delegate Lock Profile',
        template='show_stakedao_snapshot_delegate',
        body="",
        actor_profile = get_address_profile(app.config['df_actors'], delegate),
        df_locker = local_df_stakedao_delegate_agg,
        # current_votes = local_df_current_delegate_locks.iloc[0]['staked_balance'].sum(),
        local_delegations = local_delegations,
        votium_bounty_registry = app.config['votium_bounty_registry'],
        graph_list = graph_list
    )



@stakedao_snapshot_delegations_bp.route('/delegator/<string:delegator>', methods=['GET'])
def delegator(delegator):
    df_actors  = app.config['df_actors']
    df_vote_choice = app.config['df_stakedao_snapshot_vote_choice']
    # df_stakedao_locker_agg_user_epoch = app.config['df_stakedao_locker_agg_user_epoch']
    df_stakedao_delegation_locks_per_proposal = app.config['df_stakedao_delegation_locks_per_proposal']

    # Filter Data
    ## Votes
    selection = [delegator]
    mask = df_vote_choice.delegators.apply(lambda x: any(item for item in selection if item in x))
    local_df_vote_choice = df_vote_choice[mask]    
    
    local_df_vote_choice = local_df_vote_choice.sort_values(["proposal_end", 'choice_power'], axis = 0, ascending = False)

    local_df_vote_choice_self_vote = df_vote_choice[
        df_vote_choice['voter'] == delegator
        ]
    
    df_vote_temp = local_df_vote_choice[
        ~local_df_vote_choice['proposal_start'].isin(local_df_vote_choice_self_vote.proposal_start.unique())
        ]
    local_df_vote_choice = pd.concat([df_vote_temp, local_df_vote_choice_self_vote])
    local_df_vote_choice = local_df_vote_choice.sort_values(['proposal_end', 'choice_power'], ascending=False)
    ## Current Votes
    max_value = local_df_vote_choice['proposal_end'].max()
    df_current_votes = local_df_vote_choice[local_df_vote_choice['proposal_end'] == max_value]

    ## Locks
    # local_df_locker_user_epoch = df_stakedao_locker_agg_user_epoch[df_stakedao_locker_agg_user_epoch['user'] == delegator]
    
    # Locks per proposal
    local_df_stakedao_delegation_locks_per_proposal = df_stakedao_delegation_locks_per_proposal[
        df_stakedao_delegation_locks_per_proposal['delegator'] == delegator
        ]
    local_df_stakedao_delegation_locks_per_proposal = local_df_stakedao_delegation_locks_per_proposal.sort_values(['proposal_start'], ascending=False)

    if not len(local_df_stakedao_delegation_locks_per_proposal) > 0:
        return render_template(
            'delegated_staked_sdcrv_not_found.jinja2',
            title='stakedao Delegated Vote Profile',
            template='delegated_locks_not_found',
            body="",
            delegator = delegator,
            actor_profile = get_address_profile(app.config['df_actors'], delegator),
            )
    
    local_df_vote_choice_adj = adjust_delegators_votes(local_df_vote_choice, local_df_stakedao_delegation_locks_per_proposal)
    
    # Get last delegation per delegate
    local_delegations = local_df_stakedao_delegation_locks_per_proposal[
        ['delegate', 'delegate_known_as', 'proposal_start', 'proposal_title']
        ].groupby('delegate').tail(1)
    
    graph_list = []
    # # Build chart
    fig = px.pie(df_current_votes, 
                values=df_current_votes['choice_power'],
                names=df_current_votes['choice'],
                title='Current Round Gauge Distribution',
                # hover_data=['known_as'], labels={'known_as':'known_as'}
                )
    fig = format_plotly_figure(fig)
    fig.update_traces(textposition='inside', textinfo='percent')  # percent+label
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    # # Build Plotly object
    graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

    # # Build chart
    fig = px.line(local_df_vote_choice,
                    x=local_df_vote_choice['checkpoint_timestamp'],
                    y=local_df_vote_choice['available_power'],
                    # color='choice',
                    title='sdCRV Available To Delegate',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_yaxes(rangemode="tozero")
    fig = format_plotly_figure(fig)

    # # Build Plotly object
    graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

    # # Build chart
    fig = px.bar(local_df_vote_choice,
                    x=local_df_vote_choice['proposal_end'],
                    y=local_df_vote_choice['choice_power'],
                    color='choice',
                    title='Vote Distribution Per Proposal',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
        # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig = format_plotly_figure(fig)

    # # Build Plotly object
    graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

    
    # # Build chart
    fig = px.bar(local_df_stakedao_delegation_locks_per_proposal,
                    x=local_df_stakedao_delegation_locks_per_proposal['proposal_start'],
                    y=local_df_stakedao_delegation_locks_per_proposal['staked_balance'],
                    color=local_df_stakedao_delegation_locks_per_proposal['delegate_known_as'] + ' ('+local_df_stakedao_delegation_locks_per_proposal['delegate']+')' ,
                    title='Delegator Locked sdCRV by Delegate',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    fig = format_plotly_figure(fig)
    fig.update_yaxes(rangemode="tozero")

    # # Build Plotly object
    graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

    # # Build chart
    fig = px.bar(local_df_vote_choice_adj,
                    x=local_df_vote_choice_adj['checkpoint_timestamp'],
                    y=local_df_vote_choice_adj['choice_power_adj'],
                    color='choice',
                    title='sdCRV Total Delegator Vote Power by Choice',
                    # facet_row=facet_row,
                    # facet_col_wrap=facet_col_wrap
                    )
    fig = format_plotly_figure(fig)
    fig.update_yaxes(rangemode="tozero")

    # # Build Plotly object
    graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))


    return render_template(
        'show_stakedao_snapshot_delegator.jinja2',
        title='stakedao Delegated Vote Profile',
        template='snapshot-voter-show',
        body="",
        actor_profile = get_address_profile(app.config['df_actors'], delegator),
        delegator=delegator,
        df_snapshot_user = local_df_vote_choice,
        df_snapshot_user_adj = local_df_vote_choice_adj,
        local_delegations = local_delegations,
        current_votes = df_current_votes.iloc[0]['total_delegated'],
        votium_bounty_registry = app.config['votium_bounty_registry'],
        graph_list = graph_list
    )


def adjust_delegators_votes(df_local_votes, df_local_delegate_locks):
    df = pd.merge(
        df_local_votes,
        df_local_delegate_locks,
        how='left',
        left_on=['proposal_start', 'proposal_title', 'voter', 'delegate_known_as', 'delegate'],
        right_on=['proposal_start', 'proposal_title', 'delegate', 'delegate_known_as', 'delegate' ]
        ).reset_index()
    
    # Adjusts choice distribution to the vote power of the delegator
    df['choice_power_adj'] = (df['voting_weight'] / df['total_weight']) * df['staked_balance']
    df = df.rename(columns={
        "known_as_y": 'delegator_known_as',
        "known_as_x": 'known_as',
        })
    return df
