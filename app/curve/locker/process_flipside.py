from flask import current_app as app
from app.data.reference import (
    filename_curve_locker,
    known_large_cvx_holders_addresses
)
# from ... import db

from datetime import datetime as dt
from datetime import timedelta

from app.data.local_storage import (
    pd,
    read_json,
    read_csv,
    write_dataframe_csv,
    write_dfs_to_xlsx,
    csv_to_df,
    write_dataframe_csv
    )
from app.utilities.utility import (
    timed,
    get_date_obj, 
    get_dt_from_timestamp,
    # shift_time_days,
    # df_remove_nan,
    # format_plotly_figure,
    # convert_animation_to_gif,
    calc_lock_efficiency_by_checkpoint,
    nullify_amount,
)
# filename = 'crv_locker_logs'

import ast
from datetime import datetime as dt
from datetime import datetime, timedelta


from app.utilities.utility import (
    get_period, 
    get_checkpoint_end_date, 
    get_checkpoint_timestamp, 
    get_checkpoint_id,
    get_checkpoint_timestamp_from_id
)

class ProcessCurveLocker():
    def __init__(self, df):
        df = df[df['event_name'] != 'Supply']
        self.df = df
        self.processed_df = []
        self.processed_agg = []
        self.processed_known = []
        self.processed_decay = []
        self.processed_decay_agg = []
        # self.decay_ranges_x = []
        # self.decay_ranges_y = []
        # self.checkpoint_timestamps = []

        self.process_types()
        self.process_agg()
        self.process_agg_known_as()
        self.process_decay()
        pass

    @timed
    def process_types(self):
        processed_df = self.df.copy()
        # Formatting
        processed_df = processed_df[
            processed_df['event_name'].isin(['Deposit', 'Withdraw'])
            ]

        processed_df['block_timestamp'] = processed_df['block_timestamp'].apply(get_date_obj)
        processed_df['value'] = processed_df.apply(
            lambda x: nullify_amount(x['value']), 
            axis=1)
        processed_df['final_lock_time'] = processed_df['locktime'].apply(get_dt_from_timestamp)
        processed_df['known_as'] = processed_df['provider'].apply(lambda x: self.known_as(x))
        # processed_df['date'] = processed_df['block_timestamp'].apply(get_date_obj).dt.date
        # print(processed_df.head())
        processed_df['checkpoint_id'] = processed_df['block_timestamp'].apply(get_checkpoint_id)
        processed_df['checkpoint_timestamp'] = processed_df['checkpoint_id'].apply(get_checkpoint_timestamp_from_id)

        processed_df['final_checkpoint_id'] = processed_df['final_lock_time'].apply(get_checkpoint_id)
        processed_df['final_checkpoint_timestamp'] = processed_df['final_checkpoint_id'].apply(get_checkpoint_timestamp_from_id)
 
        # Apply direction of vector
        processed_df['balance_delta'] = processed_df.apply(lambda x: self.adjust_withdraws(x), axis=1)
        processed_df = processed_df.sort_values(['block_timestamp', 'final_lock_time'])

        processed_df['locked_balance'] = processed_df.groupby(
            ['provider']
            )['balance_delta'].transform(pd.Series.cumsum)
        
        # temp = processed_df.sort_values('block_timestamp').groupby(['date', 'provider']).tail(1)
        # temp['date'] = processed_df.date.max()
        # temp['balance_delta'] = 0
        # temp['tx_hash'] = None
        # temp['block_timestamp'] = dt.utcnow()
        # temp['origin_from_address'] = None

        # processed_df = pd.concat([processed_df, temp])
        processed_df = self.sort(processed_df, 'block_timestamp')
        self.processed_df = processed_df

    def sort(self, df=[], target='block_timestamp', ascend= True):
        if len(df) == 0:
            return df
        return df.sort_values([target], axis = 0, ascending = ascend)

    def adjust_withdraws(self, row):
        if row['event_name'] == 'Deposit':
            return row['value']
        elif row['event_name'] == 'Withdraw':
            return -1 * row['value']
            
    def known_as(self, user):
        if user in known_large_cvx_holders_addresses:
            return known_large_cvx_holders_addresses[user]
        else:
            return "_"
        
    @timed
    def process_agg(self):
        processed_agg = self.processed_df[['checkpoint_id', 'checkpoint_timestamp', 'balance_delta']].groupby([
                'checkpoint_id',
                'checkpoint_timestamp'
            ]).agg(
            balance_delta=pd.NamedAgg(column='balance_delta', aggfunc=sum),
        ).reset_index()
        processed_agg = self.sort(processed_agg, 'checkpoint_id')
        processed_agg['total_locked_balance'] = processed_agg['balance_delta'].transform(pd.Series.cumsum)
        self.processed_agg = processed_agg

    @timed
    def process_agg_known_as(self):
        processed_known = self.processed_df[['known_as', 'checkpoint_id', 'checkpoint_timestamp', 'balance_delta']].groupby([
                'checkpoint_id', 'known_as',
            ]).agg(
            balance_delta=pd.NamedAgg(column='balance_delta', aggfunc=sum),
        ).reset_index()

        processed_known = self.sort(processed_known, 'checkpoint_id')
        processed_known['locked_balance'] = processed_known.groupby('known_as')['balance_delta'].transform(pd.Series.cumsum)
        # set end value of current balance w/o delta from last delta

        self.processed_known = processed_known

    # def lock_efficiency(self):
        # min self.df.block_timestamp.min()
    @timed
    def process_decay(self):
        this_checkpoint = self.processed_df.checkpoint_id.min()
        max_checkpoint =  self.processed_df.checkpoint_id.max()
        output = []
        i = 0
        current_max_y_range = 0
        # ranges_x = []
        # ranges_y = []
        # checkpoint_timestamps = []
        #
        while this_checkpoint <= max_checkpoint:
            # print(f"This Checkpoint ID: {this_checkpoint}")
            this_checkpoint_timestamp = get_checkpoint_timestamp_from_id(this_checkpoint)
            # print(f"\t{this_checkpoint_timestamp}")
            # end of end of checkpoint

            # filter data set to range

            temp_df_curve_vecrv = self.processed_df.copy()
            temp_df_curve_vecrv = temp_df_curve_vecrv[temp_df_curve_vecrv['checkpoint_id'] <= this_checkpoint]
   
            # update aggregate_based info info
            temp_df_curve_vecrv['checkpoint_id'] = this_checkpoint
            temp_df_curve_vecrv['checkpoint_timestamp'] = this_checkpoint_timestamp
            
            temp_df_curve_vecrv = temp_df_curve_vecrv.groupby([
                        # 'final_lock_time',
                        'checkpoint_timestamp',
                        'checkpoint_id',
                        'provider',
                        'known_as'
                    ]).agg(
                    total_locked_balance=pd.NamedAgg(column='balance_delta', aggfunc=sum),
                    final_lock_time=pd.NamedAgg(column='final_lock_time', aggfunc=max),
                    final_checkpoint_id=pd.NamedAgg(column='final_checkpoint_id', aggfunc=max),
                    final_checkpoint_timestamp=pd.NamedAgg(column='final_checkpoint_timestamp', aggfunc=max),

                    # balance_delta=pd.NamedAgg(column='balance_delta', aggfunc=sum),
                    # total_effective_locked_balance=pd.NamedAgg(column='effective_locked_balance', aggfunc=sum),
            ).reset_index()

            this_length = len(temp_df_curve_vecrv) 

            if this_length > 0:
            # calc and apply efficiency
                temp_df_curve_vecrv['efficiency'] = temp_df_curve_vecrv.apply(
                    lambda x: calc_lock_efficiency_by_checkpoint(this_checkpoint, x['final_checkpoint_id']), axis=1
                    )
                temp_df_curve_vecrv['total_effective_locked_balance'] = temp_df_curve_vecrv['efficiency'] * temp_df_curve_vecrv['total_locked_balance'] 

            # Create informative records
            # if len(temp_df_curve_vecrv) > 0:
                # ranges_x.append([this_checkpoint_timestamp, final_checkpoint_timestamp])
                # max_bal = temp_df_curve_vecrv['total_locked_balance'].max()
                # if max_bal > current_max_y_range:
                #     ranges_y.append([0, max_bal * 1.1])
                #     current_max_y_range = max_bal
                # else:
                #     ranges_y.append([0, current_max_y_range * 1.1])

                # checkpoint_timestamps.append(this_date)

            output.append(temp_df_curve_vecrv)
            this_checkpoint = this_checkpoint + 1


        # self.decay_ranges_x = ranges_x
        # self.decay_ranges_y = ranges_y
        # self.checkpoint_timestamps = checkpoint_timestamps
        self.processed_decay = pd.concat(output)
        self.processed_decay_agg = self.processed_decay.groupby([
                'checkpoint_timestamp',
                'checkpoint_id',
            ]).agg(
                total_locked_balance=pd.NamedAgg(column='total_locked_balance', aggfunc=sum),
                total_effective_locked_balance=pd.NamedAgg(column='total_effective_locked_balance', aggfunc=sum),
            ).reset_index()
        
        
        
        
        

def process_and_save(filename= filename_curve_locker, platform='curve', asset='vecrv'):
    print("Processing... { "+platform+".locker.models }")
    ve_asset = ProcessCurveLocker(csv_to_df(filename, 'raw_data'))
    ve_asset_base = ve_asset.processed_df
    ve_asset_known = ve_asset.processed_known
    ve_asset_agg = ve_asset.processed_agg
    ve_asset_decay = ve_asset.processed_decay
    ve_asset_decay_agg = ve_asset.processed_decay_agg

    write_dataframe_csv(filename, ve_asset_base, 'processed')
    write_dataframe_csv(filename+"_known", ve_asset_known, 'processed')
    write_dataframe_csv(filename+"_agg", ve_asset_agg, 'processed')
    write_dataframe_csv(filename+"_decay", ve_asset_decay, 'processed')
    write_dataframe_csv(filename+"_decay_agg", ve_asset_decay_agg, 'processed')

    name_prefix = f"df_{platform}_{asset}"
    try:
        app.config[f"{name_prefix}"] = ve_asset_base
        app.config[f"{name_prefix}_known"] = ve_asset_known
        app.config[f"{name_prefix}_agg"] = ve_asset_agg
        app.config[f"{name_prefix}_decay"] = ve_asset_decay
        app.config[f"{name_prefix}_decay_agg"] = ve_asset_decay_agg

        # app.config['df_curve_liquidity_aggregates'] = df_curve_liquidity_aggregates
    except:
        print(f"could not register in app.config\n\t{platform} Locked {asset}")
    return {
        f"{name_prefix}" : ve_asset_base,
        f"{name_prefix}_known" : ve_asset_known,
        f"{name_prefix}_agg" : ve_asset_agg,
        f"{name_prefix}_decay" : ve_asset_decay,
        f"{name_prefix}_decay_agg" : ve_asset_decay_agg,

        # 'df_curve_liquidity_aggregates': df_curve_liquidity_aggregates,
    }

# def get_lock_diffs(final_lock_time, df = []):
#     now = datetime.now()
#     # Calc remaining lock
#     now = now.date()
#     ## Weeks until lock expires
#     if len(df)> 0:
#         final_lock_time = df.iloc[0]['final_lock_time']    
#     local_final_lock_time = final_lock_time.date()
#     diff_lock_time = local_final_lock_time - now
#     diff_lock_weeks = diff_lock_time.days / 7
#     ## Max potential weeks locked
#     four_years_forward = now + timedelta(days=(7 * 52 * 4))
#     diff_max_lock = four_years_forward - now
#     diff_max_weeks = diff_max_lock.days / 7

#     return diff_lock_weeks, diff_max_weeks