from flask import current_app as app
from app import MODELS_FOLDER_PATH, RAW_FOLDER_PATH

from app.data.reference import filename_stakedao_delegations, filename_stakedao_delegated_locks


from app.data.local_storage import (
    csv_to_df,
    df_to_csv
    )

from app.utilities.utility import print_mode

from app.convex.locker.models import (
    get_convex_locker_agg_user_epoch, 
    )

from app.snapshot.delegations.process_flipside import ProcessSnapshotDelegations

def process_and_save():
    from app.stakedao.snapshot.models import df_stakedao_snapshot_vote_choice
    from app.stakedao.staked_sdcrv.models import df_stakedao_sdcrv
    
    # df_stakedao_locker_agg_user_epoch = get_stakedao_locker_agg_user_epoch(df_stakedao_locker_user_epoch)

    print_mode("Processing... { stakedao.snapshot.delegations.models }")

    df_delegations = csv_to_df(filename_stakedao_delegations, RAW_FOLDER_PATH)
    pcb = ProcessSnapshotDelegations(df_delegations, df_stakedao_snapshot_vote_choice, df_stakedao_sdcrv, True)
    

    df_delegations = pcb.df_delegations
    df_delegated_locks_per_proposal = pcb.delegator_locks_per_proposal
    df_delegations = df_delegations.sort_values(['block_timestamp'], ascending=False)
    
    #
    # write_dataframe_csv(filename_stakedao_curve_snapshot, df_snapshot_delegated_votes, MODELS_FOLDER_PATH)
    df_to_csv(df_delegations, filename_stakedao_delegations, MODELS_FOLDER_PATH)
    df_to_csv(df_delegated_locks_per_proposal, filename_stakedao_delegated_locks, MODELS_FOLDER_PATH)

    # write_dataframe_csv(filename_stakedao_delegations+"aggregates", df_delegations_agg, MODELS_FOLDER_PATH)
    # write_dataframe_csv(filename_stakedao_locker+"_agg_user_epoch", df_snapshot_delegated_locks, MODELS_FOLDER_PATH)


    return {
        # 'df_stakedao_snapshot_vote_choice': df_snapshot_delegated_votes,
        # 'df_stakedao_locker_agg_user_epoch': df_snapshot_delegated_locks,
        'df_stakedao_delegations': df_delegations,
        'df_stakedao_delegated_locks_per_proposal': df_delegated_locks_per_proposal,
        # 'df_stakedao_delegations_agg': df_delegations_agg,

    }



# def process_and_get(save=False):
#     try:
#         df_stakedao_vote_choice = app.config['df_stakedao_snapshot_vote_choice']
#         df_stakedao_sdcrv = app.config['df_stakedao_sdcrv']

#     except:
#         from app.stakedao.snapshot.models import df_stakedao_snapshot_vote_choice as df_stakedao_vote_choice
#         from app.stakedao.staked_sdcrv.models import df_stakedao_sdcrv

        

#     print_mode("Processing... { stakedao.snapshot.delegations.models }")
#     df_delegations = csv_to_df(filename_stakedao_delegations, RAW_FOLDER_PATH)

#     pcb = ProcessSnapshotDelegations(df_delegations, df_stakedao_vote_choice, df_stakedao_sdcrv, True)

#     df_snapshot_delegated_votes = pcb.votes_with_delegate_context
#     df_snapshot_delegated_locks = pcb.locks_with_delegate_context
#     # print(f"Length Locks: {len(df_snapshot_delegated_locks)}")
#     df_delegations = pcb.df_delegations
#     df_delegations = df_delegations.sort_values(['block_timestamp'], ascending=False)
#     df_delegations_agg = pcb.aggregate_delegates
#     df_delegation_locks_per_proposal = pcb.delegator_locks_per_proposal
    
#     #
#     if save:
#         pass
#         # write_dataframe_csv(filename_stakedao_curve_snapshot, df_snapshot_delegated_votes, MODELS_FOLDER_PATH)
#         # write_dataframe_csv(filename_stakedao_locker+"_agg_user_epoch", df_snapshot_delegated_locks, MODELS_FOLDER_PATH)
#         # write_dataframe_csv(filename_stakedao_delegations, df_delegations, MODELS_FOLDER_PATH)
#         # write_dataframe_csv(filename_stakedao_delegations+"aggregates", df_delegations_agg, MODELS_FOLDER_PATH)
#     try:
#         # app.config['df_active_votes'] = df_active_votes
#         app.config['df_stakedao_snapshot_vote_choice'] = df_snapshot_delegated_votes
#         # app.config['df_stakedao_locker_agg_user_epoch'] = df_snapshot_delegated_locks
#         app.config['df_stakedao_delegations'] = df_delegations
#         app.config['df_stakedao_delegations_agg'] = df_delegations_agg
#         app.config['df_stakedao_delegation_locks_per_proposal'] = df_delegation_locks_per_proposal


#     except:
#         print_mode("could not register in app.config\n\tstakedao Snapshot Delegations")
#     return {
#         # 'df_active_votes': df_active_votes,
#         'df_stakedao_snapshot_vote_choice': df_snapshot_delegated_votes,
#         # 'df_stakedao_locker_agg_user_epoch': df_snapshot_delegated_locks,
#         'df_stakedao_delegations': df_delegations,
#         'df_stakedao_delegations_agg': df_delegations_agg,
#         'df_stakedao_delegation_locks_per_proposal': df_delegation_locks_per_proposal,

#     }