from flask import current_app as app
from app.data.reference import filename_convex_delegations , filename_convex_locker, known_large_cvx_holders_addresses

from datetime import datetime as dt
from datetime import datetime, timedelta
from app.utilities.utility import timed
import traceback

from app.data.local_storage import (
    pd,
    read_json, 
    read_csv,  
    write_dataframe_csv,
    write_dfs_to_xlsx
    )
# from app.utilities.utility import get_period

from app.utilities.utility import (
    # get_period_direct, 
    # get_period_end_date, 
    get_date_obj, 
    get_dt_from_timestamp,
    shift_time_days,
    df_remove_nan,
    get_now
)
# try:
#     df_convex_snapshot_vote_choice = app.config['df_convex_snapshot_vote_choice']

# except:
#     from app.convex.snapshot.models import df_convex_snapshot_vote_choice


class ProcessConvexLocker():
    def __init__(self, df_locker):
        self.df_locker = df_locker
        # self.df_locker_aggregate = []
        
        self.df_user_epoch = [] # All locks
        self.df_aggregate_user_epoch = []   # Sum of locks per lock per epoch per user
        self.df_aggregate_system = [] # Aggregate sum of locks per epoch
        self.df_aggregate_epoch = [] # Aggregate sum of locks per user per epoch
        self.df_aggregate_epoch_current = [] # only current aggregate epoch
        self.process()
        self.process_user_epoch()
        self.process_aggregate_user_epoch()
        self.process_aggregate_system()
        self.process_aggregate_epoch()
        self.sort_locker()


    def process(self):
        self.df_locker['locked_amount'] = self.df_locker['locked_amount'].astype(float)
        self.df_locker['epoch_start'] = self.df_locker.apply(
            lambda x: get_dt_from_timestamp(x['_epoch']), 
            axis=1)
        
        
        
        self.df_locker['epoch_end'] = self.df_locker['epoch_start'].apply(lambda x: shift_time_days(x,16*7))
        self.df_locker['known_as'] = self.df_locker['user'].apply(lambda x: self.known_as(x))
        self.df_locker['display_name'] = self.df_locker.apply(lambda x: self.display_name(x['user'], x['known_as']), axis=1)
    
    def known_as(self, user):
        if user in known_large_cvx_holders_addresses:
            return known_large_cvx_holders_addresses[user]
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
    
    # Calculate total balance of locks at each epoch per user
    def process_aggregate_user_epoch(self):
        self.df_aggregate_user_epoch = self.df_user_epoch.groupby([
                'this_epoch', 'user', 'known_as', 'display_name'
            ]).agg(
            current_locked=pd.NamedAgg(column='current_locked', aggfunc=sum),
            lock_count=pd.NamedAgg(column='lock_count', aggfunc=sum)
        ).reset_index()
        return
    
    # Calculate total locked per epoch (sum all locks within an epoch)
    # And create filter for only currently locked epochs
    def process_aggregate_epoch(self):
        self.df_aggregate_epoch = self.df_locker.groupby([
                'epoch_start',
                'epoch_end',
            ]).agg(
            locked_amount=pd.NamedAgg(column='locked_amount', aggfunc=sum),
            lock_count=pd.NamedAgg(column='tx_hash', aggfunc=lambda x: len(x.unique())

        )).reset_index()
        now_epoch = self.df_aggregate_epoch[self.df_aggregate_epoch['epoch_start'] <= get_now()].epoch_start.max()
        # temp = self.df_aggregate_epoch 
        self.df_aggregate_epoch_current = self.df_aggregate_epoch[self.df_aggregate_epoch['epoch_end'] >= now_epoch]
        return
    
    
    # Calculate total locked each epoch (sum all currently active epochs) 
    def process_aggregate_system(self):
        self.df_aggregate_system = self.df_aggregate_user_epoch.groupby([
                'this_epoch',
            ]).agg(
            total_locked=pd.NamedAgg(column='current_locked', aggfunc=sum),
            lock_count=pd.NamedAgg(column='lock_count', aggfunc=sum),
            user_count=pd.NamedAgg(column='user', aggfunc=lambda x: len(x.unique()))
        ).reset_index()
        return

def get_df_convex_locks():
    filename = filename_convex_locker    #+ fallback_file_title
    resp_dict = read_csv(filename, 'raw_data')
    df = pd.json_normalize(resp_dict)
    try:
        df = df.sort_values("block_timestamp", axis = 0, ascending = True)
    except:
        df = df.sort_values("BLOCK_TIMESTAMP", axis = 0, ascending = True)
    return df   

def process_and_save():
    print("Processing... { convex.locker.models }")
    pcl = ProcessConvexLocker(get_df_convex_locks())
    pcl_base = pcl.df_locker
    pcl_user = pcl.df_user_epoch
    pcl_agg_user = pcl.df_aggregate_user_epoch
    pcl_agg_system = pcl.df_aggregate_system
    pcl_agg_epoch = pcl.df_aggregate_epoch
    pcl_agg_current = pcl.df_aggregate_epoch_current

    write_dataframe_csv(filename_convex_locker, pcl_base, 'processed')
    write_dataframe_csv(filename_convex_locker+"_user_epoch", pcl_user, 'processed')
    write_dataframe_csv(filename_convex_locker+"_agg_user_epoch", pcl_agg_user, 'processed')
    write_dataframe_csv(filename_convex_locker+"_agg_system", pcl_agg_system, 'processed')
    write_dataframe_csv(filename_convex_locker+"_agg_epoch", pcl_agg_epoch, 'processed')
    write_dataframe_csv(filename_convex_locker+"_agg_current", pcl_agg_current, 'processed')

    try:
        app.config['df_convex_locker'] = pcl_base
        app.config['df_convex_user_epoch'] = pcl_user
        app.config['df_convex_agg_user'] = pcl_agg_user
        app.config['df_convex_agg_system'] = pcl_agg_system
        app.config['df_convex_agg_epoch'] = pcl_agg_epoch
        app.config['df_convex_agg_current'] = pcl_agg_current

        # app.config['df_curve_liquidity_aggregates'] = df_curve_liquidity_aggregates
    except:
        print("could not register in app.config\n\tConvex Locker")
    return {
        'df_convex_locker': pcl_base,
        'df_convex_user_epoch': pcl_user,

        # 'df_curve_liquidity_aggregates': df_curve_liquidity_aggregates,
    }