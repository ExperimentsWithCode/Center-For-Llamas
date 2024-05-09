from flask import current_app as app
from app import MODELS_FOLDER_PATH

from app.data.reference import filename_convex_locker, filename_convex_locker_user_epoch

from app.data.local_storage import (
    pd,
    csv_to_df
    )


from app.utilities.utility import (
 
    get_date_obj, 
    get_dt_from_timestamp,
    nullify_amount,
    print_mode,
    get_now

)



print_mode("Loading... { convex.locker.models }")


def format_df(df_in):
    df = df_in.copy()
    key_list = df.keys()
    if 'block_timestamp' in key_list:
        df['block_timestamp'] = df['block_timestamp'].apply(get_date_obj)

    if 'locked_amount' in key_list:
        df['locked_amount'] = df.apply(
            lambda x: nullify_amount(x['locked_amount']), 
            axis=1)
    if '_epoch' in key_list:
        df['epoch_start'] = df['_epoch'].apply(get_dt_from_timestamp)
    
    elif 'epoch_start' in key_list:
        df['epoch_start'] = pd.to_datetime(df['epoch_start'])

    if 'epoch_end' in key_list:
        # df['epoch_end'] = df['epoch_end'].apply(get_dt_from_timestamp)
        df['epoch_end'] = pd.to_datetime(df['epoch_end'])

    if 'this_epoch' in key_list:
        # df['epoch_end'] = df['epoch_end'].apply(get_dt_from_timestamp)
        df['this_epoch'] = pd.to_datetime(df['this_epoch'])

    # if 'checkpoint' in key_list:
    #     df['checkpoint'] = df['checkpoint'].apply(get_dt_from_timestamp)

    if 'current_locked' in key_list:
        df['current_locked'] = df.apply(
            lambda x: nullify_amount(x['current_locked']), 
            axis=1)

    if 'withdrawn_amount' in key_list:
        df['withdrawn_amount'] = df.apply(
            lambda x: nullify_amount(x['withdrawn_amount']), 
            axis=1)
        
    if 'lock_count' in key_list:
        df['lock_count'] = df['lock_count'].astype(int)

    # if 'liquidity_over_votes' in key_list:
    #     df['liquidity_over_votes'] = df['liquidity_over_votes'].astype(float)

    # if 'liquidity_native_over_votes' in key_list:
    #     df['liquidity_over_votes'] = df['liquidity_over_votes'].astype(float)

    return df

def get_df(filename, location):
    df = csv_to_df(filename, location)
    df = format_df(df)
    return df

df_locker = get_df(filename_convex_locker, MODELS_FOLDER_PATH)
df_locker_user_epoch = get_df(filename_convex_locker_user_epoch, MODELS_FOLDER_PATH)

try:
    app.config['df_convex_locker'] = df_locker
    app.config['df_convex_locker_user_epoch'] = df_locker_user_epoch
    # app.config['df_convex_locker_agg_user_epoch'] = df_locker_agg_user_epoch
    # app.config['df_convex_locker_agg_system'] = df_locker_agg_system
    # app.config['df_convex_locker_agg_epoch'] = df_locker_agg_epoch
    # app.config['df_convex_locker_agg_current'] = df_locker_agg_current
except:
    print_mode("could not register in app.config\n\tConvex Locker")


# Calculate total balance of locks at each epoch per user
def get_convex_locker_agg_user_epoch(df_locker_user_epoch):
    return df_locker_user_epoch.groupby([
            'this_epoch', 'user', 'known_as', 'display_name'
        ]).agg(
        current_locked=pd.NamedAgg(column='current_locked', aggfunc=sum),
        lock_count=pd.NamedAgg(column='lock_count', aggfunc=sum)
        ).reset_index()

# Calculate total locked per epoch (sum all locks within an epoch)
def get_convex_locker_agg_epoch(df_locker):
    return df_locker.groupby([
            'epoch_start',
            'epoch_end',
        ]).agg(
        locked_amount=pd.NamedAgg(column='locked_amount', aggfunc=sum),
        lock_count=pd.NamedAgg(column='tx_hash', aggfunc=lambda x: len(x.unique())

        )).reset_index()

# Calculate total locked each epoch (sum all currently active epochs) 
def get_convex_locker_agg_system(df_aggregate_user_epoch=[]):
    if len(df_aggregate_user_epoch) == 0:
        df_aggregate_user_epoch = get_convex_locker_agg_user_epoch()
    return df_aggregate_user_epoch.groupby([
            'this_epoch',
        ]).agg(
        total_locked=pd.NamedAgg(column='current_locked', aggfunc=sum),
        lock_count=pd.NamedAgg(column='lock_count', aggfunc=sum),
        user_count=pd.NamedAgg(column='user', aggfunc=lambda x: len(x.unique()))
        ).reset_index()

# create filter for only currently locked epochs
def get_convex_locker_agg_current(df_locker_agg_epoch=[]):
    if len(df_locker_agg_epoch) == 0:
        df_locker_agg_epoch = get_convex_locker_agg_epoch()
    # now_epoch = df_locker_agg_epoch[df_locker_agg_epoch['epoch_start'] <= get_now()].epoch_start.max()
    return df_locker_agg_epoch[df_locker_agg_epoch['epoch_end'] >= get_now()]