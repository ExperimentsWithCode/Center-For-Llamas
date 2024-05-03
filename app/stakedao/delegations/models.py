from flask import current_app as app
from app import MODELS_FOLDER_PATH

from app.data.reference import (
    filename_stakedao_delegations, 
    filename_stakedao_delegated_locks
    )

from app.data.local_storage import (
    pd,
    csv_to_df
    )


from app.utilities.utility import (
    get_date_obj, 
    get_dt_from_timestamp,
    nullify_amount,
    nullify_list,
    print_mode
)

from app.snapshot.delegations.models import format_df, bind_snapshot_context_to_delegations

try: 
    df_stakedao_snapshot_vote_choice = app.config['df_stakedao_snapshot_vote_choice']
except:
    from app.stakedao.snapshot.models import df_stakedao_snapshot_vote_choice
 
print_mode("Loading... { stakedao.delegation.models }")


def get_df(filename, location):
    df = csv_to_df(filename, location)
    df = format_df(df)
    return df

def get_stakedao_delegate_agg(df_stakedao_delegated_locks_per_proposal=[]):
    if len(df_stakedao_delegated_locks_per_proposal) == 0:
        df_stakedao_delegated_locks_per_proposal = get_df(filename_stakedao_delegated_locks, MODELS_FOLDER_PATH)
    df = df_stakedao_delegated_locks_per_proposal.groupby([
            'proposal_start',
            'proposal_title',
            'delegate_known_as',
            'delegate',
        ]).agg(
            total_delegated=pd.NamedAgg(column='staked_balance', aggfunc=sum),
            # delegated_lock_count=pd.NamedAgg(column='lock_count', aggfunc=sum),
            delegators_count=pd.NamedAgg(column='delegator', aggfunc=lambda x: len(x.unique())),
            delegators=pd.NamedAgg(column='delegator', aggfunc=list),
            known_delegators=pd.NamedAgg(column='delegator_known_as', aggfunc=list),
        ).reset_index()
    df['delegators'] = df['delegators'].apply(lambda x: nullify_list(x))
    df['known_delegators'] = df['known_delegators'].apply(lambda x: nullify_list(x, True))
    return df
    # Convex Version
    # df = df_stakedao_delegated_locks_per_proposal.groupby([
    #         'proposal_start',
    #         'proposal_title',
    #         'delegate_known_as',
    #         'delegate',
    #         'this_epoch'
    #     ]).agg(
    #     total_delegated=pd.NamedAgg(column='current_locked', aggfunc=sum),
    #     delegated_lock_count=pd.NamedAgg(column='lock_count', aggfunc=sum),
    #     delegators_count=pd.NamedAgg(column='delegator', aggfunc=lambda x: len(x.unique())),
    #     delegators=pd.NamedAgg(column='delegator', aggfunc=list),
    #     known_delegators=pd.NamedAgg(column='delegator_known_as', aggfunc=list),
    # ).reset_index()
    # df['delegators'] = df['delegators'].apply(lambda x: nullify_list(x))
    # df['known_delegators'] = df['known_delegators'].apply(lambda x: nullify_list(x, True))
    # aggregate_delegates = df
    # return

df_stakedao_delegations = get_df(filename_stakedao_delegations, MODELS_FOLDER_PATH)
df_stakedao_delegated_locks_per_proposal = get_df(filename_stakedao_delegated_locks, MODELS_FOLDER_PATH)

df_stakedao_delegations_agg = get_stakedao_delegate_agg(df_stakedao_delegated_locks_per_proposal)
df_stakedao_snapshot_vote_choice = bind_snapshot_context_to_delegations(
    df_stakedao_snapshot_vote_choice, 
    df_stakedao_delegations_agg
    )

def load():
    try:
        app.config['df_stakedao_delegations'] = df_stakedao_delegations
        app.config['df_stakedao_delegated_locks_per_proposal'] = df_stakedao_delegated_locks_per_proposal
        app.config['df_stakedao_delegations_agg'] = df_stakedao_delegations_agg
        app.config['df_stakedao_snapshot_vote_choice'] = df_stakedao_snapshot_vote_choice

    except:
        print_mode("could not register in app.config\n\tConvex Delegations")
    return {
        'df_stakedao_delegations': df_stakedao_delegations,
        'df_stakedao_delegated_locks_per_proposal': df_stakedao_delegated_locks_per_proposal,
        'df_stakedao_snapshot_vote_choice': df_stakedao_snapshot_vote_choice
    }

load()
