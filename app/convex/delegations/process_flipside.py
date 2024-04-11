from flask import current_app as app


from app.data.reference import filename_convex_delegations, filename_convex_curve_snapshot, filename_convex_locker

from app.snapshot.delegations.process_flipside import ProcessSnapshotDelegations

from app.data.local_storage import (
    pd,
    csv_to_df,
    write_dataframe_csv
    )

try:
    df_convex_snapshot_vote_choice = app.config['df_convex_snapshot_vote_choice']
    df_convex_locker_agg_user_epoch = app.config['df_convex_locker_agg_user_epoch']

except:
    from app.convex.snapshot.models import df_convex_snapshot_vote_choice
    from app.convex.locker.models import df_locker_agg_user_epoch as df_convex_locker_agg_user_epoch

    

def process_and_get(save=False):
    try:
    from config import activate_print_mode
except:
    activate_print_mode = False

if activate_print_mode:
    print("Processing... { convex.snapshot.delegations.models }")
    df_delegations = csv_to_df(filename_convex_delegations, 'raw_data')

    pcb = ProcessSnapshotDelegations(df_delegations, df_convex_snapshot_vote_choice, df_convex_locker_agg_user_epoch)

    df_snapshot_delegated_votes = pcb.votes_with_delegate_context
    df_snapshot_delegated_locks = pcb.locks_with_delegate_context
    # print(f"Length Locks: {len(df_snapshot_delegated_locks)}")
    df_delegations = pcb.df_delegations
    df_delegations = df_delegations.sort_values(['block_timestamp'], ascending=False)
    df_delegations_agg = pcb.aggregate_delegates
    df_delegation_locks_per_proposal = pcb.delegator_locks_per_proposal
    
    #
    if save:
        pass
        # write_dataframe_csv(filename_convex_curve_snapshot, df_snapshot_delegated_votes, 'processed')
        # write_dataframe_csv(filename_convex_locker+"_agg_user_epoch", df_snapshot_delegated_locks, 'processed')
        # write_dataframe_csv(filename_convex_delegations, df_delegations, 'processed')
        # write_dataframe_csv(filename_convex_delegations+"aggregates", df_delegations_agg, 'processed')
    try:
        # app.config['df_active_votes'] = df_active_votes
        app.config['df_convex_snapshot_vote_choice'] = df_snapshot_delegated_votes
        # app.config['df_convex_locker_agg_user_epoch'] = df_snapshot_delegated_locks
        app.config['df_convex_delegations'] = df_delegations
        app.config['df_convex_delegations_agg'] = df_delegations_agg
        app.config['df_convex_delegation_locks_per_proposal'] = df_delegation_locks_per_proposal


    except:
        print("could not register in app.config\n\tConvex Snapshot Delegations")
    return {
        # 'df_active_votes': df_active_votes,
        'df_convex_snapshot_vote_choice': df_snapshot_delegated_votes,
        # 'df_convex_locker_agg_user_epoch': df_snapshot_delegated_locks,
        'df_convex_delegations': df_delegations,
        'df_convex_delegations_agg': df_delegations_agg,
        'df_convex_delegation_locks_per_proposal': df_delegation_locks_per_proposal,

    }

# def process_and_save():
#     try:
    from config import activate_print_mode
except:
    activate_print_mode = False

if activate_print_mode:
    print("Processing... { convex.snapshot.delegations.models }")
#     df_delegations = csv_to_df(filename_convex_delegations, 'raw_data')

#     pcb = ProcessSnapshotDelegations(df_delegations, df_convex_snapshot_vote_choice, df_convex_locker_agg_user_epoch)

#     df_snapshot_delegated_votes = pcb.votes_with_delegate_context
#     df_snapshot_delegated_locks = pcb.locks_with_delegate_context
#     print(f"Length Locks: {len(df_snapshot_delegated_locks)}")
#     df_delegations = pcb.df_delegations
#     df_delegations_agg = pcb.aggregate_delegates

#     # write_dataframe_csv(filename_convex_curve_snapshot, df_snapshot_delegated_votes, 'processed')
#     # write_dataframe_csv(filename_convex_locker, df_snapshot_delegated_locks, 'processed')
#     # write_dataframe_csv(filename_convex_delegations, df_delegations, 'processed')
#     # write_dataframe_csv(filename_convex_delegations+"aggregates", df_delegations_agg, 'processed')
#     try:
#         # app.config['df_active_votes'] = df_active_votes
#         app.config['df_convex_snapshot_vote_choice'] = df_snapshot_delegated_votes
#         app.config['df_convex_locker_agg_user_epoch'] = df_snapshot_delegated_locks
#         app.config['df_convex_delegations'] = df_delegations
#         app.config['df_convex_delegations_agg'] = df_delegations_agg

#     except:
#         print("could not register in app.config\n\tConvex Snapshot Delegations")
#     return {
#         # 'df_active_votes': df_active_votes,
#         'df_convex_snapshot_vote_choice': df_snapshot_delegated_votes,
#         'df_convex_locker_agg_user_epoch': df_snapshot_delegated_locks,
#         'df_convex_delegations': df_delegations,
#         'df_convex_delegations_agg': df_delegations_agg,
#     }