from flask import current_app as app
from app import MODELS_FOLDER_PATH


from app.data.reference import filename_convex_curve_snapshot, filename_convex_curve_snapshot_origin



from app.data.local_storage import (
    pd,
    csv_to_df
    )

# filename = 'crv_locker_logs'

from app.utilities.utility import print_mode
from app.data.source.legacy_proposal_choice_map import convex_snapshot_proposal_choice_map
from app.snapshot.votes.models import format_df

print_mode("Loading... { convex.snapshot.models }")


def get_df_snapshot_vote_choice():
    filename = filename_convex_curve_snapshot # + current_file_title
    df_snapshot = csv_to_df(filename, MODELS_FOLDER_PATH)
    df_snapshot = df_snapshot[~df_snapshot['proposal_title'].str.contains('FXN')]
    df_snapshot = format_df(df_snapshot)
    return df_snapshot.sort_values("timestamp", axis = 0, ascending = True)
    
    
def get_convex_snapshot_aggregates(df_vote_choice):
    df_vote_aggregates = df_vote_choice.groupby(
        ['checkpoint_id', 'checkpoint_timestamp','proposal_start', 'proposal_end', 'proposal_title', 'choice', 'choice_index', 'gauge_addr']
        )['choice_power'].agg(['sum','count']).reset_index()

    df_vote_aggregates = df_vote_aggregates.rename(columns={
        "sum": 'total_vote_power',
        'count': 'cvx_voter_count'})
    df_vote_aggregates =df_vote_aggregates.sort_values(["proposal_end", 'total_vote_power', 'gauge_addr'], axis = 0, ascending = False)
    return df_vote_aggregates


df_convex_snapshot_vote_choice = get_df_snapshot_vote_choice()
df_convex_snapshot_vote_aggregates = get_convex_snapshot_aggregates(df_convex_snapshot_vote_choice)

try:
    app.config['convex_snapshot_proposal_choice_map'] = convex_snapshot_proposal_choice_map
    app.config['df_convex_snapshot_vote_aggregates'] = df_convex_snapshot_vote_aggregates
    app.config['df_convex_snapshot_vote_choice'] = df_convex_snapshot_vote_choice
except:
    print_mode("could not register in app.config\n\tConvex Snapshot")
