from flask import current_app as app
from app.data.reference import (
    filename_curve_gauge_rounds_by_user,
    filename_curve_gauge_rounds_by_aggregate, 
)

from app.data.local_storage import (
    pd,
    read_json,
    read_csv,
    write_dataframe_csv,
    write_dfs_to_xlsx,
    csv_to_df
    )


print("Loading... { curve.gauge_rounds.models }")

def format_df(df):
    key_list = df.keys()
    # df['gauge_addr']            = df['gauge_addr'].astype(str)
    # df['gauge_name']            = df['gauge_name'].astype(str)
    # df['gauge_symbol']          = df['gauge_symbol'].astype(str)
    # df['pool_addr']             = df['pool_addr'].astype(str)
    # df['pool_name']             = df['pool_name'].astype(str)
    # df['pool_symbol']           = df['pool_symbol'].astype(str)
    # df['pool_partial']          = df['pool_partial'].astype(str)
    # df['token_addr']            = df['token_addr'].astype(str)
    # df['token_name']            = df['token_name'].astype(str)
    # df['token_symbol']          = df['token_symbol'].astype(str)
    # df['source']                = df['source'].astype(str)
    # df['deployed_timestamp']    = df['deployed_timestamp'].astype(str)
    # df['first_period']          = df['first_period'].astype(str)
    # df['first_period_end_date'] = df['first_period_end_date'].astype(str)

    # All
    if 'block_number' in key_list:
        df['block_number']          = df['block_number'].astype(int)
    if 'block_timetamp' in key_list:
        df['block_timetamp']        = pd.to_datetime(df['block_timetamp'])
    if 'timestamp' in key_list:
        df['timestamp']             = pd.to_datetime(df['timestamp'])
    if 'time' in key_list:
        df['time']                  = pd.to_datetime(df['time'])
    if 'final_lock_time' in key_list:
        df['final_lock_time']       = pd.to_datetime(df['final_lock_time'])

    # if 'period_end_date' in key_list:
    #     df['period_end_date']       = pd.to_datetime(df['period_end_date']).dt.date


    if 'total_vote_power' in key_list:
        df['total_vote_power']      = df['total_vote_power'].astype(float)
    if 'vecrv_voter_count' in key_list:
        df['vecrv_voter_count']     = df['vecrv_voter_count'].astype(int)


    if 'weight' in key_list:
        df['weight']                = df['weight'].astype(int)
    if 'balance' in key_list:
        df['balance']               = df['balance'].astype(str)
    if 'locked_crv' in key_list:
        df['locked_crv']           = df['locked_crv'].astype(float)

    if 'vote_percent' in key_list:
        df['vote_percent']          = pd.to_numeric(df.vote_percent, errors='coerce')

    if 'vote_power' in key_list:
        df['vote_power']            = pd.to_numeric(df.vote_power, errors='coerce')

    if 'total_vote_percent' in key_list:
        df['total_vote_percent']    = pd.to_numeric(df.total_vote_percent, errors='coerce')

    if 'total_vote_power' in key_list:
        df['total_vote_power']      = pd.to_numeric(df.total_vote_power, errors='coerce')


    if 'vote_power_raw' in key_list:
        df['vote_power_raw']            = pd.to_numeric(df.vote_power_raw, errors='coerce')

    if 'vote_utilization' in key_list:
        df['vote_utilization']      = pd.to_numeric(df.vote_utilization, errors='coerce')

    if 'checkpoint_id' in key_list:
        df['checkpoint_id']       = df['checkpoint_id'].astype(int)
    if 'checkpoint_timestamp' in key_list:
        df['checkpoint_timestamp']       = pd.to_datetime(df['checkpoint_timestamp'])

    if 'final_checkpoint_id' in key_list:
        df['final_checkpoint_id']       = pd.to_numeric(df.final_checkpoint_id, errors='coerce')
    if 'final_checkpoint_timestamp' in key_list:
        df['final_checkpoint_timestamp']       = pd.to_datetime(df['final_checkpoint_timestamp'])


    if 'vote_checkpoint_id' in key_list:
        df['vote_checkpoint_id']       = pd.to_numeric(df.vote_checkpoint_id, errors='coerce')
    if 'vote_checkpoint_timestamp' in key_list:
        df['vote_checkpoint_timestamp']       = pd.to_datetime(df['vote_checkpoint_timestamp'])
    if 'vote_timestamp' in key_list:
        df['vote_timestamp']       = pd.to_datetime(df['vote_timestamp'])

    if 'lock_checkpoint_id' in key_list:
        df['lock_checkpoint_id']       = pd.to_numeric(df.lock_checkpoint_id, errors='coerce')
    if 'lock_checkpoint_timestamp' in key_list:
        df['lock_checkpoint_timestamp']       = pd.to_datetime(df['lock_checkpoint_timestamp'])
    if 'lock_timestamp' in key_list:
        df['lock_timestamp']       = pd.to_datetime(df['lock_timestamp'])


    if 'efficiency' in key_list:
        df['efficiency']       = pd.to_numeric(df.efficiency, errors='coerce')

    return df


def get_df(filename):
    df = csv_to_df(filename, 'processed')
    df = format_df(df)
    return df

df_checkpoints = get_df(filename_curve_gauge_rounds_by_user)
df_checkpoints_agg = get_df(filename_curve_gauge_rounds_by_aggregate) 


try:
    app.config['df_checkpoints'] = df_checkpoints
    app.config['df_checkpoints_agg'] = df_checkpoints_agg
except:
    print("could not register in app.config\n\tGauge Rounds")




# Index(['known_as_x', 
#     'voter', 
#     'gauge_addr', 
#     'user', 
#     'time', 
#     'weight', 
#     'name',
#     'symbol', 
#     'period', 
#     'period_end_date', 
#     'checkpoint_id_x',
#     'checkpoint_timestamp_x', 
#     'checkpoint_timestamp_y', 
#     'checkpoint_id_y',
#     'provider', 
#     'known_as_y', 
#     'total_locked_balance', 
#     'final_lock_time',
#     'final_checkpoint_id', 
#     'final_checkpoint_timestamp', 
#     'efficiency',
#     'total_effective_locked_balance', 
#     'vote_power_raw', 
#     'vote_power',
#     'checkpoint_id', 
#     'checkpoint_timestamp', 
#     'vote_percent'
#     ],
#     dtype='object')