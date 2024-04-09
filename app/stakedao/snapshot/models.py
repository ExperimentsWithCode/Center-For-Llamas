from app.data.reference import filename_stakedao_curve_snapshot, filename_stakedao_curve_snapshot_origin


try:
    from flask import current_app as app
except:
    pass

from app.data.local_storage import (
    pd,
    read_json,
    read_csv,
    csv_to_df,
    write_dataframe_csv,
    write_dfs_to_xlsx
    )

# filename = 'crv_locker_logs'


import traceback


from app.data.reference import known_large_market_actors

from app.snapshot.models import Snapshot
from app.snapshot.alt_models import merge_target


try:
    gauge_registry = app.config['gauge_registry']
except:
    from app.curve.gauges.models import gauge_registry



print("Loading... { stakedao.snapshot.models }")



def get_df_snapshot():
    filename = filename_stakedao_curve_snapshot # + current_file_title
    try:
        df_snapshot = csv_to_df(filename, 'raw_data')
        return df_snapshot.sort_values("vote_timestamp", axis = 0, ascending = True)
    except:
        snapshot_dict = read_json(filename, 'raw_data')
        df_snapshot = pd.json_normalize(snapshot_dict)
        return df_snapshot.sort_values("VOTE_TIMESTAMP", axis = 0, ascending = True)
    
# def get_df_snapshot_from_snapshot():
#     filename = filename_stakedao_curve_snapshot_origin
#     return csv_to_df(filename)


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
        ['checkpoint_id', 'checkpoint_timestamp', 'proposal_start', 'proposal_end', 'proposal_title', 'choice', 'choice_index', 'gauge_addr']
        )['choice_power'].agg(['sum','count']).reset_index()

    df_vote_aggregates = df_vote_aggregates.rename(columns={
        "sum": 'total_vote_power',
        'count': 'sdcrv_voter_count'})
    df_vote_aggregates =df_vote_aggregates.sort_values(["proposal_end", 'total_vote_power'], axis = 0, ascending = False)

    # dfs.append(df_vote_aggregates)
    # titles.append('Aggregates')
    return df_vote_aggregates


df_snapshot = get_df_snapshot()
snapshot = get_snapshot_obj(df_snapshot)
df_stakedao_snapshot_vote_choice_temp = get_df_vote_choice(snapshot)

stakedao_snapshot_proposal_choice_map = snapshot.format_choice_map_output()

a, b= merge_target(df_stakedao_snapshot_vote_choice_temp, stakedao_snapshot_proposal_choice_map, 'stakedao')
df_stakedao_snapshot_vote_choice = a
stakedao_snapshot_proposal_choice_map = b 

df_stakedao_snapshot_vote_aggregates = get_aggregates(df_stakedao_snapshot_vote_choice)


try:
    app.config['stakedao_snapshot_proposal_choice_map'] = stakedao_snapshot_proposal_choice_map
    app.config['df_stakedao_snapshot_vote_aggregates'] = df_stakedao_snapshot_vote_aggregates
    app.config['df_stakedao_snapshot_vote_choice'] = df_stakedao_snapshot_vote_choice
except:
    print("could not register in app.config\n\tSnapshot")

# print(stakedao_snapshot_proposal_choice_map)