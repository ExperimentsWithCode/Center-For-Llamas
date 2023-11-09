from flask import current_app as app
from app.data.reference import filename_convex_locker, filename_convex_locker_aggregate

from app.data.local_storage import (
    pd,
    read_json,
    read_csv,
    write_dataframe_csv,
    write_dfs_to_xlsx,
    csv_to_df
    )


from app.utilities.utility import (
    get_period_direct, 
    get_period_end_date, 
    get_date_obj, 
    get_dt_from_timestamp,
    shift_time_days,
    df_remove_nan
)


print("Loading... { convex.locker.models }")


def format_df(df):
    key_list = df.keys()

    if 'locked_amount' in key_list:
        df['locked_amount'] = df['locked_amount'].astype(float)

    if 'epoch_start' in key_list:
        df['epoch_start'] = df['_epoch'].apply(get_dt_from_timestamp)
    
    if 'epoch_end' in key_list:
        df['epoch_end'] = df['epoch_end'].apply(get_dt_from_timestamp)

    if 'checkpoint' in key_list:
        df['checkpoint'] = df['checkpoint'].apply(get_dt_from_timestamp)

    if 'current_lock' in key_list:
        df['current_lock'] = df['current_lock'].astype(float)

    if 'lock_count' in key_list:
        df['lock_count'] = df['lock_count'].astype(int)

    # if 'liquidity_over_votes' in key_list:
    #     df['liquidity_over_votes'] = df['liquidity_over_votes'].astype(float)

    # if 'liquidity_native_over_votes' in key_list:
    #     df['liquidity_over_votes'] = df['liquidity_over_votes'].astype(float)

    return df

def get_df(filename):
    df = csv_to_df(filename, 'processed')
    df = format_df(df)
    return df

df_locker = get_df(filename_convex_locker, 'processed')
df_locker_user_epoch = get_df(filename_convex_locker+"_user_epoch", 'processed')
df_locker_agg_user_epoch = get_df(filename_convex_locker+"_agg_user_epoch", 'processed')
df_locker_agg_system = get_df(filename_convex_locker+"_agg_system", 'processed')
df_locker_agg_epoch = get_df(filename_convex_locker+"_agg_epoch", 'processed')
df_locker_agg_current = get_df(filename_convex_locker+"_agg_current", 'processed')


try:
    app.config['df_convex_locker'] = df_locker
    app.config['df_convex_locker_user_epoch'] = df_locker_user_epoch
    app.config['df_convex_locker_agg_user_epoch'] = df_locker_agg_user_epoch
    app.config['df_convex_locker_agg_system'] = df_locker_agg_system
    app.config['df_convex_locker_agg_epoch'] = df_locker_agg_epoch
    app.config['df_convex_locker_agg_current'] = df_locker_agg_current
except:
    print("could not register in app.config\n\tConvex Locker")



