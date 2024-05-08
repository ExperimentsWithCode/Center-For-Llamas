from flask import current_app as app
from app import MODELS_FOLDER_PATH, RAW_FOLDER_PATH
from app.data.reference import (
    filename_convex_delegations, 
    filename_convex_delegated_locks
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


print_mode("Loading... { convex.delegation.models }")

try: 
    df_convex_snapshot_vote_choice = app.config['df_convex_snapshot_vote_choice']
except:
    from app.convex.snapshot.models import df_convex_snapshot_vote_choice

def get_df(filename, location):
    df = csv_to_df(filename, location)
    df = format_df(df)
    return df

def get_convex_delegate_agg(df_convex_delegated_locks_per_proposal=[]):
    if len(df_convex_delegated_locks_per_proposal) == 0:
        df_convex_delegated_locks_per_proposal = get_df(filename_convex_delegated_locks, MODELS_FOLDER_PATH)

    df = df_convex_delegated_locks_per_proposal.groupby([
            'proposal_start',
            'proposal_title',
            'delegate_known_as',
            'delegate',
            'this_epoch'
        ]).agg(
        total_delegated=pd.NamedAgg(column='current_locked', aggfunc=sum),
        delegated_lock_count=pd.NamedAgg(column='lock_count', aggfunc=sum),
        delegators_count=pd.NamedAgg(column='delegator', aggfunc=lambda x: len(x.unique())),
        delegators=pd.NamedAgg(column='delegator', aggfunc=list),
        known_delegators=pd.NamedAgg(column='delegator_known_as', aggfunc=list),
    ).reset_index()
    df['delegators'] = df['delegators'].apply(lambda x: nullify_list(x))
    df['known_delegators'] = df['known_delegators'].apply(lambda x: nullify_list(x, True))
    return df
    return
    # StakeDAO Version
        # df = self.delegator_locks_per_proposal.groupby([
        #         'proposal_start',
        #         'proposal_title',
        #         'delegate_known_as',
        #         'delegate',
        #     ]).agg(
        #         total_delegated=pd.NamedAgg(column='staked_balance', aggfunc=sum),
        #         # delegated_lock_count=pd.NamedAgg(column='lock_count', aggfunc=sum),
        #         delegators_count=pd.NamedAgg(column='delegator', aggfunc=lambda x: len(x.unique())),
        #         delegators=pd.NamedAgg(column='delegator', aggfunc=list),
        #         known_delegators=pd.NamedAgg(column='delegator_known_as', aggfunc=list),
        #     ).reset_index()
        # df['delegators'] = df['delegators'].apply(lambda x: nullify_list(x))
        # df['known_delegators'] = df['known_delegators'].apply(lambda x: nullify_list(x, True))
        # self.aggregate_delegates = df
        # return

def bind_snapshot_context_to_delegations(df_snapshot_votes, aggregate_delegates):
    df = pd.merge(
        df_snapshot_votes,
        aggregate_delegates,
        how='left',
        left_on=['proposal_title', 'proposal_start', 'voter'],
        right_on=['proposal_title', 'proposal_start', 'delegate' ]
    ).reset_index()
    df['delegators'] = df['delegators'].apply(lambda x: nullify_list(x))
    df['known_delegators'] = df['known_delegators'].apply(lambda x: nullify_list(x, True))
    return df



df_convex_delegations = get_df(filename_convex_delegations, MODELS_FOLDER_PATH)
df_convex_delegated_locks_per_proposal = get_df(filename_convex_delegated_locks, MODELS_FOLDER_PATH)

df_convex_delegations_agg = get_convex_delegate_agg(df_convex_delegated_locks_per_proposal)
df_convex_snapshot_vote_choice = bind_snapshot_context_to_delegations(df_convex_snapshot_vote_choice, df_convex_delegations_agg)


try:
    app.config['df_convex_delegations'] = df_convex_delegations
    app.config['df_convex_delegated_locks_per_proposal'] = df_convex_delegated_locks_per_proposal
    # app.config['df_convex_delegations_agg'] = df_convex_delegations_agg
    app.config['df_convex_snapshot_vote_choice'] = df_convex_snapshot_vote_choice

except:
    print_mode("could not register in app.config\n\tConvex Delegations")

