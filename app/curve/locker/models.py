from flask import current_app as app
from app import MODELS_FOLDER_PATH
from app.data.reference import (
    filename_curve_locker,
    filename_curve_locker_decay,
)

from datetime import datetime as dt
from datetime import timedelta

from app.data.local_storage import (
    pd,
    csv_to_df
    )

from app.utilities.utility import (
    get_date_obj, 
    timed,
    print_mode,
    get_now,
    # nullify_amount,
)
 
print_mode("Loading... { curve.locker.models }")

def get_lock_diffs(final_lock_time, df = []):
    now = get_now()
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

    if 'block_timetamp' in key_list:
        df['block_timestamp']       = df['block_timestamp'].apply(get_date_obj)

    if 'final_lock_time' in key_list:
        df['final_lock_time']        =df['final_lock_time'].apply(get_date_obj)

    if 'checkpoint_date' in key_list:
        df['checkpoint_date']       = pd.to_datetime(df['checkpoint_date']).dt.date


    if 'value' in key_list:
        df['value']       = df['value'].astype(float)

    if 'balance_delta' in key_list:
        df['balance_delta']       = df['balance_delta'].astype(float)

    if 'total_balance_delta' in key_list:
        df['total_balance_delta']       = df['total_balance_delta'].astype(float)

    if 'total_locked_balance' in key_list:
        df['total_locked_balance']       = df['total_locked_balance'].astype(float)

    if 'locked_balance' in key_list:
        df['locked_balance']       = df['locked_balance'].astype(float)

    if 'total_effective_locked_balance' in key_list:
        df['total_effective_locked_balance']       = df['total_effective_locked_balance'].astype(float)

    if 'effective_locked_balance' in key_list:
        df['effective_locked_balance']       = df['effective_locked_balance'].astype(float)

    if 'checkpoint_id' in key_list:
        df['checkpoint_id']       = df['checkpoint_id'].astype(int)
    if 'checkpoint_timestamp' in key_list:
        df['checkpoint_timestamp']       = pd.to_datetime(df['checkpoint_timestamp'])
    if 'final_checkpoint_id' in key_list:
        df['final_checkpoint_id']       = df['final_checkpoint_id'].astype(int)
    if 'final_checkpoint_timestamp' in key_list:
        df['final_checkpoint_timestamp']       = pd.to_datetime(df['final_checkpoint_timestamp'])
    if 'efficiency' in key_list:
        df['efficiency']       = df['efficiency'].astype(float)
    return df


def get_df(filename):
    df = csv_to_df(filename, MODELS_FOLDER_PATH)
    df = format_df(df)
    return df


# df_curve_vecrv = get_df(filename_curve_locker)
# df_curve_vecrv_known = process_agg_known_as(df_curve_vecrv) 
# df_curve_vecrv_agg = process_agg(df_curve_vecrv)
# df_curve_vecrv_decay = get_df(filename_curve_locker + '_decay')
# df_curve_vecrv_decay_agg = process_decay_agg(df_curve_vecrv_decay)

df_curve_vecrv = get_df(filename_curve_locker)
# df_curve_vecrv_known = get_df(filename_curve_locker + '_known') 
# df_curve_vecrv_agg = get_df(filename_curve_locker + '_agg')
df_curve_vecrv_decay = get_df(filename_curve_locker_decay)
# df_curve_vecrv_decay_agg = get_df(filename_curve_locker_decay + '_agg')

platform = 'curve'
asset = 'vecrv'
name_prefix = f"df_{platform}_{asset}"
try:
    app.config[f"{name_prefix}"] = df_curve_vecrv
    # app.config[f"{name_prefix}_known"] = df_curve_vecrv_known
    # app.config[f"{name_prefix}_agg"] = df_curve_vecrv_agg
    app.config[f"{name_prefix}_decay"] = df_curve_vecrv_decay
    # app.config[f"{name_prefix}_decay_agg"] = df_curve_vecrv_decay_agg
except:
    print_mode("could not register in app.config\n\Curve Locked veCRV")
