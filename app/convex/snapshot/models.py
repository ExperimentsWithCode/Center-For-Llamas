from app.data.reference import filename_convex_curve_snapshot, filename_convex_curve_snapshot_origin


try:
    from flask import current_app as app
except:
    pass

from app.data.local_storage import (
    pd,
    read_json,
    read_csv,
    write_dataframe_csv,
    write_dfs_to_xlsx,
    csv_to_df
    )

# filename = 'crv_locker_logs'

from app.snapshot.models import Snapshot
from app.snapshot.alt_models import merge_target
from app.utilities.utility import print_mode
 
print_mode("Loading... { convex.snapshot.models }")


def get_df_snapshot():
    filename = filename_convex_curve_snapshot # + current_file_title
    try:
        df_snapshot = csv_to_df(filename, 'raw_data')
        df_snapshot = df_snapshot[~df_snapshot['proposal_title'].str.contains('FXN')]
        return df_snapshot.sort_values("vote_timestamp", axis = 0, ascending = True)
    except:
        snapshot_dict = read_json(filename, 'raw_data')
        df_snapshot = pd.json_normalize(snapshot_dict)
        df_snapshot = df_snapshot[~df_snapshot['PROPOSAL_TITLE'].str.contains('FXN')]
        return df_snapshot.sort_values("VOTE_TIMESTAMP", axis = 0, ascending = True)
    

def get_snapshot_obj(df_snapshot):
    snapshot = Snapshot()
    snapshot.process(df_snapshot)
    return snapshot

def get_df_vote_choice(snapshot):
    vote_choice_data = snapshot.format_final_choice_output()
    df_vote_choice = pd.json_normalize(vote_choice_data)
    return df_vote_choice.sort_values("proposal_start", axis = 0, ascending = True)


def get_aggregates(df_vote_choice):
    df_vote_aggregates = df_vote_choice.groupby(
        ['checkpoint_id', 'checkpoint_timestamp','proposal_start', 'proposal_end', 'proposal_title', 'choice', 'choice_index', 'gauge_addr']
        )['choice_power'].agg(['sum','count']).reset_index()

    df_vote_aggregates = df_vote_aggregates.rename(columns={
        "sum": 'total_vote_power',
        'count': 'cvx_voter_count'})
    df_vote_aggregates =df_vote_aggregates.sort_values(["proposal_end", 'total_vote_power', 'gauge_addr'], axis = 0, ascending = False)

    return df_vote_aggregates


df_snapshot = get_df_snapshot()
snapshot = get_snapshot_obj(df_snapshot)
df_convex_snapshot_vote_choice = get_df_vote_choice(snapshot)

convex_snapshot_proposal_choice_map = snapshot.format_choice_map_output()

a, b= merge_target(df_convex_snapshot_vote_choice, convex_snapshot_proposal_choice_map, 'convex')
df_convex_snapshot_vote_choice = a
convex_snapshot_proposal_choice_map = b 

df_convex_snapshot_vote_aggregates = get_aggregates(df_convex_snapshot_vote_choice)
# write_dataframe_csv('df_convex_snapshot_vote_choice', df_convex_snapshot_vote_choice)

try:
    app.config['convex_snapshot_proposal_choice_map'] = convex_snapshot_proposal_choice_map
    app.config['df_convex_snapshot_vote_aggregates'] = df_convex_snapshot_vote_aggregates
    app.config['df_convex_snapshot_vote_choice'] = df_convex_snapshot_vote_choice
except:
    print_mode("could not register in app.config\n\tSnapshot")

# print(convex_snapshot_proposal_choice_map)
