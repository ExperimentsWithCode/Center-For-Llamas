try:
    from flask import current_app as app
except:
    pass

from app.data.local_storage import (
    pd,
    read_json,
    read_csv,
    write_dataframe_csv,
    write_dfs_to_xlsx
    )

# filename = 'crv_locker_logs'

from app.snapshot.models import Snapshot


def get_df_snapshot():
    try:
        filename = 'convex_snapshot_votes' # + current_file_title
        snapshot_dict = read_csv(filename, 'source')
        df_snapshot = pd.json_normalize(snapshot_dict)
        return df_snapshot.sort_values("vote_timestamp", axis = 0, ascending = True)
    except:
        filename = 'convex_snapshot_votes' #+ fallback_file_title
        snapshot_dict = read_json(filename, 'source')
        df_snapshot = pd.json_normalize(snapshot_dict)
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
    # dfs = []
    # titles = []
    # for title in df_vote_choice.proposal_title.unique():
    #     df_temp = df_vote_choice[
    #         df_vote_choice.proposal_title.isin([title])
    #     ]
    #     dfs.append(df_temp)
    #     titles.append(title)

    df_vote_aggregates = df_vote_choice.groupby(
        ['period', 'period_end_date', 'proposal_end', 'proposal_title', 'choice', 'choice_index']
        )['choice_power'].agg(['sum','count']).reset_index()

    df_vote_aggregates = df_vote_aggregates.rename(columns={
        "sum": 'total_vote_power',
        'count': 'cvx_voter_count'})
    df_vote_aggregates =df_vote_aggregates.sort_values(["proposal_end", 'total_vote_power'], axis = 0, ascending = False)

    # dfs.append(df_vote_aggregates)
    # titles.append('Aggregates')
    return df_vote_aggregates


df_snapshot = get_df_snapshot()
snapshot = get_snapshot_obj(df_snapshot)
df_convex_snapshot_vote_choice = get_df_vote_choice(snapshot)
df_convex_snapshot_vote_aggregates = get_aggregates(df_convex_snapshot_vote_choice)

convex_snapshot_proposal_choice_map = snapshot.format_choice_map_output()


try:
    app.config['convex_snapshot_proposal_choice_map'] = convex_snapshot_proposal_choice_map
    app.config['df_convex_snapshot_vote_aggregates'] = df_convex_snapshot_vote_aggregates
    app.config['df_convex_snapshot_vote_choice'] = df_convex_snapshot_vote_choice
except:
    print("could not register in app.config\n\tSnapshot")

# print(convex_snapshot_proposal_choice_map)
