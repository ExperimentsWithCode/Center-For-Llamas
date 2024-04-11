from flask import current_app as app


from app.data.reference import filename_stakedao_delegations, filename_stakedao_curve_snapshot, filename_stakedao_staked_sdcrv

from app.snapshot.delegations.process_flipside import ProcessSnapshotDelegations

from app.data.local_storage import (
    pd,
    csv_to_df,
    write_dataframe_csv
    )

try:
    df_stakedao_vote_choice = app.config['df_stakedao_snapshot_vote_choice']
    df_stakedao_sdcrv = app.config['df_stakedao_sdcrv']

except:
    from app.stakedao.snapshot.models import df_stakedao_snapshot_vote_choice as df_stakedao_vote_choice
    from app.stakedao.staked_sdcrv.models import df_stakedao_sdcrv

    


def process_and_get(save=False):
    print("Processing... { stakedao.snapshot.delegations.models }")
    df_delegations = csv_to_df(filename_stakedao_delegations, 'raw_data')

    pcb = ProcessSnapshotDelegations(df_delegations, df_stakedao_vote_choice, df_stakedao_sdcrv, True)

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
        # write_dataframe_csv(filename_stakedao_curve_snapshot, df_snapshot_delegated_votes, 'processed')
        # write_dataframe_csv(filename_stakedao_locker+"_agg_user_epoch", df_snapshot_delegated_locks, 'processed')
        # write_dataframe_csv(filename_stakedao_delegations, df_delegations, 'processed')
        # write_dataframe_csv(filename_stakedao_delegations+"aggregates", df_delegations_agg, 'processed')
    try:
        # app.config['df_active_votes'] = df_active_votes
        app.config['df_stakedao_snapshot_vote_choice'] = df_snapshot_delegated_votes
        # app.config['df_stakedao_locker_agg_user_epoch'] = df_snapshot_delegated_locks
        app.config['df_stakedao_delegations'] = df_delegations
        app.config['df_stakedao_delegations_agg'] = df_delegations_agg
        app.config['df_stakedao_delegation_locks_per_proposal'] = df_delegation_locks_per_proposal


    except:
        print("could not register in app.config\n\tstakedao Snapshot Delegations")
    return {
        # 'df_active_votes': df_active_votes,
        'df_stakedao_snapshot_vote_choice': df_snapshot_delegated_votes,
        # 'df_stakedao_locker_agg_user_epoch': df_snapshot_delegated_locks,
        'df_stakedao_delegations': df_delegations,
        'df_stakedao_delegations_agg': df_delegations_agg,
        'df_stakedao_delegation_locks_per_proposal': df_delegation_locks_per_proposal,

    }
# def process_and_save():
#     print("Processing... { convex.snapshot.delegations.models }")
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