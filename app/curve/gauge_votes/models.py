from flask import current_app as app
from app import MODELS_FOLDER_PATH

from app.data.reference import (
    filename_curve_gauge_votes,
    filename_curve_gauge_votes,
    filename_curve_gauge_votes_formatted,
    filename_curve_gauge_votes_current
)

from app.data.local_storage import (
    pd,
    read_json,
    read_csv,
    write_dataframe_csv,
    write_dfs_to_xlsx,
    csv_to_df
    )

from app.utilities.utility import print_mode
print_mode("Loading... { curve.gauges_votes.models }")


def format_df(df):
    key_list = df.keys()
    if 'weight' in key_list:
        df['weight']               = df['weight'].astype(int)
    if 'period_end_date' in key_list:
        df['period_end_date'] = pd.to_datetime(df['period_end_date']).dt.date
    if 'checkpoint_timestamp' in key_list:
        df['checkpoint_timestamp'] = pd.to_datetime(df['checkpoint_timestamp'])
    if 'block_timestamp' in key_list:
        df['block_timestamp'] = pd.to_datetime(df['block_timestamp'])
    if 'checkpoint_id' in key_list:
        df['checkpoint_id'] = df['checkpoint_id'].astype(int)
    return df


def get_df(filename):
    try:
        df = csv_to_df(filename, MODELS_FOLDER_PATH)
        df = format_df(df)
    except:
        gauge_pool_map = read_json(filename, MODELS_FOLDER_PATH)
        df = pd.json_normalize(gauge_pool_map)
        df = format_df(df)

    # df_gauge_pool_map = df_gauge_pool_map.sort_values("BLOCK_TIMESTAMP", axis = 0, ascending = True)
    return df

def get_current_votes(df_gauge_votes_formatted):
    df_current_gauge_votes = df_gauge_votes_formatted.groupby(['voter', 'gauge_addr'], as_index=False).last()
    df_current_gauge_votes = df_current_gauge_votes[df_current_gauge_votes['weight'] > 0]
    df_current_gauge_votes = df_current_gauge_votes.sort_values("time", axis = 0, ascending = False)
    return df_current_gauge_votes


df_all_votes = get_df(filename_curve_gauge_votes)
df_gauge_votes_formatted = get_df(filename_curve_gauge_votes_formatted)
df_current_gauge_votes = get_current_votes(df_gauge_votes_formatted)

try:
    # app.config['df_active_votes'] = df_active_votes
    app.config['df_all_votes'] = df_all_votes
    app.config['df_gauge_votes_formatted'] = df_gauge_votes_formatted
    # app.config['df_current_gauge_votes'] = df_current_gauge_votes
except:
    print_mode("could not register in app.config\n\tGauge Votes")