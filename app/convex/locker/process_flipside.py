from flask import current_app as app
from app import MODELS_FOLDER_PATH, RAW_FOLDER_PATH

from app.data.reference import (
    filename_convex_locker, 
    filename_convex_locker_user_epoch,
    known_large_market_actors
)

from datetime import datetime as dt
from datetime import datetime, timedelta
from app.utilities.utility import timed

from app.data.local_storage import (
    pd,
    df_to_csv,  
    csv_to_df
    )
# from app.utilities.utility import get_period

from app.utilities.utility import (
    get_date_obj, 
    get_dt_from_timestamp,
    shift_time_days,
    df_remove_nan,
    get_now,
    nullify_amount,
    print_mode

)


class ProcessConvexLocker():
    def __init__(self, df_locker):
        self.df_locker = df_locker
        # self.df_locker_aggregate = []
        
        self.df_user_epoch = [] # All locks
        self.df_aggregate_user_epoch = []   # Sum of locks per lock per epoch per user
        self.df_aggregate_system = [] # Aggregate sum of locks per epoch
        self.df_aggregate_epoch = [] # Aggregate sum of locks per user per epoch
        self.process()
        self.process_user_epoch()
        # self.process_aggregate_user_epoch()
        # self.process_aggregate_system()
        # self.process_aggregate_epoch()
        self.sort_locker()


    def process(self):
        self.df_locker['locked_amount'] = self.df_locker.apply(
            lambda x: nullify_amount(x['locked_amount']), 
            axis=1)
        self.df_locker['epoch_start'] = self.df_locker.apply(
            lambda x: get_dt_from_timestamp(x['_epoch']), 
            axis=1)
        self.df_locker['epoch_end'] = self.df_locker['epoch_start'].apply(lambda x: shift_time_days(x,16*7))
        self.df_locker['known_as'] = self.df_locker['user'].apply(lambda x: self.known_as(x))
        self.df_locker['display_name'] = self.df_locker.apply(lambda x: self.display_name(x['user'], x['known_as']), axis=1)
    
    def known_as(self, user):
        if user in known_large_market_actors:
            return known_large_market_actors[user]
        else:
            return "_"

    def sort_locker(self):
        self.df_locker = self.df_locker.sort_values("block_timestamp", axis = 0, ascending = False)


    def display_name(self, user, known_as ):
        # print(user)
        # print(known_as)
        if known_as:
            return f"{known_as} ({user[:6]})"
        else:
            return f"({user[:6]})"

    # Calculate total balance for individual locks at each epoch per user
    def process_user_epoch(self, df=[]):
        if len(df) == 0:
            df = self.df_locker
        furthest_epoch = df.epoch_end.max()
        this_epoch = df.epoch_start.min()
        local_list = []
        while this_epoch <= furthest_epoch:
            this_epoch_buff = shift_time_days(this_epoch, 1)
            df_local = df[df['epoch_start'] <= this_epoch_buff ]
            df_local = df_local[df_local['epoch_end'] > this_epoch_buff ]
            df_local = df_local.groupby([
                    'epoch_start', 'epoch_end', 'user', 'known_as', 'display_name',
                ])['locked_amount'].agg(['sum', 'count']).reset_index()
            df_local = df_local.rename(columns={
                        "sum": 'current_locked',
                        "count": 'lock_count'
                        })
            df_local['this_epoch'] = this_epoch
            local_list.append(df_local)
            this_epoch = shift_time_days(this_epoch, 7)
        self.df_user_epoch = pd.concat(local_list)
        return
    
def get_df_convex_locks():
    filename = filename_convex_locker    #+ fallback_file_title
    df = csv_to_df(filename, RAW_FOLDER_PATH)
    df = df.sort_values("block_timestamp", axis = 0, ascending = True)
    return df   

def process_and_save():
    print_mode("Processing... { convex.locker.models }")
    pcl = ProcessConvexLocker(get_df_convex_locks())
    pcl_base = pcl.df_locker
    pcl_user = pcl.df_user_epoch

    df_to_csv(pcl_base, filename_convex_locker, MODELS_FOLDER_PATH)
    df_to_csv(pcl_user, filename_convex_locker_user_epoch, MODELS_FOLDER_PATH)

    return {
        'df_convex_locker': pcl_base,
        'df_convex_user_epoch': pcl_user,

    }