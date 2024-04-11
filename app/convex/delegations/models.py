from flask import current_app as app
from app.data.reference import filename_convex_delegations, filename_convex_curve_snapshot, filename_convex_locker

from app.data.local_storage import (
    pd,
    # read_json,
    # read_csv,
    # write_dataframe_csv,
    # write_dfs_to_xlsx,
    csv_to_df
    )


from app.utilities.utility import (
    # get_period_direct, 
    # get_period_end_date, 
    get_date_obj, 
    get_dt_from_timestamp,
    nullify_amount
    # shift_time_days,
    # df_remove_nan
)

from app.convex.delegations.process_flipside import process_and_get

try:
    from config import activate_print_mode
except:
    activate_print_mode = False

if activate_print_mode:
    print("Loading... { convex.locker.models }")


def format_df(df):
    # key_list = df.keys()
    # if 'block_timestamp' in key_list:
    #     df['block_timestamp'] = df['block_timestamp'].apply(get_date_obj)

    # if 'locked_amount' in key_list:
    #     df['locked_amount'] = df.apply(
    #         lambda x: nullify_amount(x['locked_amount']), 
    #         axis=1)
    # if '_epoch' in key_list:
    #     df['epoch_start'] = df['_epoch'].apply(get_dt_from_timestamp)
    
    # elif 'epoch_start' in key_list:
    #     df['epoch_start'] = pd.to_datetime(df['epoch_start'])

    # if 'epoch_end' in key_list:
    #     # df['epoch_end'] = df['epoch_end'].apply(get_dt_from_timestamp)
    #     df['epoch_end'] = pd.to_datetime(df['epoch_end'])

    # if 'this_epoch' in key_list:
    #     # df['epoch_end'] = df['epoch_end'].apply(get_dt_from_timestamp)
    #     df['this_epoch'] = pd.to_datetime(df['this_epoch'])

    # if 'checkpoint' in key_list:
    #     df['checkpoint'] = df['checkpoint'].apply(get_dt_from_timestamp)

    # if 'current_locked' in key_list:
    #     df['current_locked'] = df.apply(
    #         lambda x: nullify_amount(x['current_locked']), 
    #         axis=1)

    # if 'lock_count' in key_list:
    #     df['lock_count'] = df['lock_count'].astype(int)

    # if 'liquidity_over_votes' in key_list:
    #     df['liquidity_over_votes'] = df['liquidity_over_votes'].astype(float)

    # if 'liquidity_native_over_votes' in key_list:
    #     df['liquidity_over_votes'] = df['liquidity_over_votes'].astype(float)

    return df

# def get_df(filename, location):
#     df = csv_to_df(filename, location)
#     df = format_df(df)
#     return df

df_map = process_and_get()
# df_locker = get_df(filename_convex_locker, 'processed')
# df_locker_user_epoch = get_df(filename_convex_locker+"_user_epoch", 'processed')
df_convex_snapshot_vote_choice = df_map['df_convex_snapshot_vote_choice']
# df_convex_locker_agg_user_epoch = df_map['df_convex_locker_agg_user_epoch']
df_convex_delegations = df_map['df_convex_delegations']
df_convex_delegations_agg = df_map['df_convex_delegations_agg']
df_convex_delegation_locks_per_proposal = df_map['df_convex_delegation_locks_per_proposal']



try:
    app.config['df_convex_snapshot_vote_choice'] = df_convex_snapshot_vote_choice
    # app.config['df_convex_locker_agg_user_epoch'] = df_convex_locker_agg_user_epoch
    app.config['df_convex_delegations'] = df_convex_delegations
    app.config['df_convex_delegations_agg'] = df_convex_delegations_agg
    app.config['df_convex_delegation_locks_per_proposal'] = df_convex_delegation_locks_per_proposal

except:
    print("could not register in app.config\n\tConvex Delegations")



