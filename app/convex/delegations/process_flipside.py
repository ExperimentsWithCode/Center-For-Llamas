from flask import current_app as app
from app import MODELS_FOLDER_PATH, RAW_FOLDER_PATH


from app.data.reference import filename_convex_delegations, filename_convex_delegated_locks


from app.data.local_storage import (
    pd,
    csv_to_df,
    df_to_csv
    )

from app.utilities.utility import print_mode

from app.convex.locker.models import (
    get_convex_locker_agg_user_epoch, 
    )

from app.snapshot.delegations.process_flipside import ProcessSnapshotDelegations






def process_and_save():
    from app.convex.snapshot.models import df_convex_snapshot_vote_choice
    from app.convex.locker.models import (
    get_convex_locker_agg_user_epoch, 
    df_locker_user_epoch
    )
    df_convex_locker_agg_user_epoch = get_convex_locker_agg_user_epoch(df_locker_user_epoch)

    print_mode("Processing... { convex.snapshot.delegations.models }")

    df_delegations = csv_to_df(filename_convex_delegations, RAW_FOLDER_PATH)
    pcb = ProcessSnapshotDelegations(df_delegations, df_convex_snapshot_vote_choice, df_convex_locker_agg_user_epoch)
    

    df_delegations = pcb.df_delegations
    df_delegated_locks_per_proposal = pcb.delegator_locks_per_proposal
    df_delegations = df_delegations.sort_values(['block_timestamp'], ascending=False)
    
    #
    # write_dataframe_csv(filename_convex_curve_snapshot, df_snapshot_delegated_votes, MODELS_FOLDER_PATH)
    df_to_csv(df_delegations, filename_convex_delegations,  MODELS_FOLDER_PATH)
    df_to_csv(df_delegated_locks_per_proposal, filename_convex_delegated_locks, MODELS_FOLDER_PATH)

    # write_dataframe_csv(filename_convex_delegations+"aggregates", df_delegations_agg, MODELS_FOLDER_PATH)
    # write_dataframe_csv(filename_convex_locker+"_agg_user_epoch", df_snapshot_delegated_locks, MODELS_FOLDER_PATH)


    return {
        # 'df_convex_snapshot_vote_choice': df_snapshot_delegated_votes,
        # 'df_convex_locker_agg_user_epoch': df_snapshot_delegated_locks,
        'df_convex_delegations': df_delegations,
        'df_convex_delegated_locks_per_proposal': df_delegated_locks_per_proposal,
        # 'df_convex_delegations_agg': df_delegations_agg,

    }

