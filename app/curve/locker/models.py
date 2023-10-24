from flask import current_app as app
from app.data.reference import (
    filename_curve_locker_supply,
    filename_curve_locker_withdraw, 
    filename_curve_locker_deposit,
    filename_curve_locker_history,
    filename_curve_locker_current_locks, 
    filename_curve_locker_known_locks 
)

from datetime import datetime as dt
from datetime import timedelta

from app.data.local_storage import (
    pd,
    read_json,
    read_csv,
    write_dataframe_csv,
    write_dfs_to_xlsx,
    csv_to_df
    )


print("Loading... { curve.locker.models }")

def get_lock_diffs(final_lock_time, df = []):
    now = dt.now()
    # Calc remaining lock
    now = now.date()
    ## Weeks until lock expires
    if len(df)> 0:
        final_lock_time = df.iloc[0]['final_lock_time']    
    local_final_lock_time = final_lock_time.date()
    diff_lock_time = local_final_lock_time - now
    diff_lock_weeks = diff_lock_time.days / 7
    ## Max potential weeks locked
    four_years_forward = now + timedelta(days=(7 * 52 * 4))
    diff_max_lock = four_years_forward - now
    diff_max_weeks = diff_max_lock.days / 7

    return diff_lock_weeks, diff_max_weeks

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
    if 'final_lock_time' in key_list:
        df['final_lock_time']        = pd.to_datetime(df['final_lock_time'])
    if 'timestamp' in key_list:
        df['timestamp']             = pd.to_datetime(df['timestamp'])
    if 'period_end_date' in key_list:
        df['period_end_date']       = pd.to_datetime(df['period_end_date']).dt.date
    if 'ts' in key_list:
        df['ts']                    = df['ts'].astype(int)
    if 'balance_adj' in key_list:
        df['balance_adj']           = df['balance_adj'].astype(float)
    # Supply
    if 'prevSupply' in key_list:
        df['prevSupply']            = df['prevSupply'].astype(float)
    if 'supply' in key_list:
        df['supply']                = df['supply'].astype(str)
    # Deposit
    if 'locktime' in key_list:
        df['locktime']              = df['locktime'].astype(float)
    if 'type' in key_list:
        df['type']                  = df['type'].astype(float)
    if 'balance_adj' in key_list:
        df['balance_adj']           = df['balance_adj'].astype(float)
    return df


def get_df(filename):
    df = csv_to_df(filename, 'processed')
    df = format_df(df)
    return df

df_curve_locker_supply = get_df(filename_curve_locker_supply)
df_curve_locker_withdraw = get_df(filename_curve_locker_withdraw) 
df_curve_locker_deposit = get_df(filename_curve_locker_deposit)
df_curve_locker_history = get_df(filename_curve_locker_history)
df_curve_locker_current_locks = get_df(filename_curve_locker_current_locks)
df_curve_locker_known_locks = get_df(filename_curve_locker_known_locks) 

try:
    app.config['df_curve_locker_supply'] = df_curve_locker_supply
    app.config['df_curve_locker_withdraw'] = df_curve_locker_withdraw
    app.config['df_curve_locker_deposit'] = df_curve_locker_deposit

    app.config['df_curve_locker_history'] = df_curve_locker_history
    app.config['df_curve_locker_current_locks'] = df_curve_locker_current_locks

    app.config['df_curve_locker_known_locks'] = df_curve_locker_known_locks
except:
    print("could not register in app.config\n\tGauges")