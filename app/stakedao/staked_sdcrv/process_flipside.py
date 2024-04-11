from flask import current_app as app
from app.data.reference import filename_stakedao_staked_sdcrv , known_large_market_actors

from datetime import datetime as dt
from datetime import datetime, timedelta
from app.utilities.utility import timed
import traceback

from app.data.local_storage import (
    pd,
    read_json, 
    read_csv,  
    csv_to_df,
    write_dataframe_csv,
    write_dfs_to_xlsx
    )
from app.utilities.utility import get_period

from app.utilities.utility import (
    get_period_direct, 
    get_period_end_date, 
    get_date_obj, 
    get_dt_from_timestamp,
    shift_time_days,
    df_remove_nan
)



class StakeDAOsdCRV():
    def __init__(self, df):
        self.df = self.sort(df)
        self.processed_df = []
        self.processed_agg = []
        self.processed_known = []
        self.process_df()
        self.process_agg()
        self.process_agg_known_as()

    def sort(self, df=[], target='block_timestamp'):
        if len(df) == 0:
            return df
        return df.sort_values([target], axis = 0, ascending = True)

    def adjust_withdraws(self, row):
        if row['event_name'] == 'Deposit':
            return row['value']
        elif row['event_name'] == 'Withdraw':
            return -1 * row['value']
        elif row['event_name'] == 'Transfer':
            return row['value']

        
    def known_as(self, user):
        if user in known_large_market_actors:
            return known_large_market_actors[user]
        else:
            return "_"
        
    def process_df(self):
        processed_df = self.df.copy()

        processed_df['value'] = processed_df['value'].astype(float)
        processed_df['known_as'] = processed_df['provider'].apply(lambda x: self.known_as(x))

        processed_df['balance_delta'] = processed_df.apply(lambda x: self.adjust_withdraws(x), axis=1)
        processed_df = processed_df.sort_values('block_timestamp')

        processed_df['staked_balance'] = processed_df.groupby(
            ['provider']
            )['balance_delta'].transform(pd.Series.cumsum)
        
        processed_df['date'] = processed_df['block_timestamp'].apply(get_date_obj).dt.date


        temp = processed_df.sort_values('date').groupby(['provider']).tail(1)
        temp['date'] = temp.date.max()
        temp['balance_delta'] = 0

        processed_df = pd.concat([processed_df, temp])
        processed_df = self.sort(processed_df, 'block_timestamp')

        self.processed_df = processed_df

    def process_agg(self):
        processed_agg = self.processed_df[['date', 'balance_delta']].groupby([
                'date'
            ]).agg(
            balance_delta=pd.NamedAgg(column='balance_delta', aggfunc=sum),
        ).reset_index()
        processed_agg = self.sort(processed_agg, 'date')
        processed_agg['total_staked_balance'] = processed_agg['balance_delta'].transform(pd.Series.cumsum)
        self.processed_agg = processed_agg


    def process_agg_known_as(self):
        processed_known = self.processed_df[['known_as', 'date', 'balance_delta']].groupby([
                'date', 'known_as'
            ]).agg(
            balance_delta=pd.NamedAgg(column='balance_delta', aggfunc=sum),
        ).reset_index()

        processed_known = self.sort(processed_known, 'date')
        processed_known['staked_balance'] = processed_known.groupby('known_as')['balance_delta'].transform(pd.Series.cumsum)
        # set end value of current balance w/o delta from last delta

        self.processed_known = processed_known


def get_df(filename):
    df = csv_to_df(filename, 'raw_data')

    # df_gauge_pool_map = df_gauge_pool_map.sort_values("BLOCK_TIMESTAMP", axis = 0, ascending = True)
    return df

def process_and_save():
    print("Processing... { stakedao.sdcrv.models }")
    sdcrv = StakeDAOsdCRV(get_df(filename_stakedao_staked_sdcrv))
    sdcrv_base = sdcrv.processed_df
    sdcrv_known = sdcrv.processed_known
    sdcrv_agg = sdcrv.processed_agg
    write_dataframe_csv(filename_stakedao_staked_sdcrv, sdcrv_base, 'processed')
    write_dataframe_csv(filename_stakedao_staked_sdcrv+"_known", sdcrv_known, 'processed')
    write_dataframe_csv(filename_stakedao_staked_sdcrv+"_agg", sdcrv_agg, 'processed')

    try:
        app.config['df_stakedao_sdcrv'] = sdcrv_base
        app.config['df_stakedao_sdcrv_known'] = sdcrv_known
        app.config['df_stakedao_sdcrv_agg'] = sdcrv_agg

        # app.config['df_curve_liquidity_aggregates'] = df_curve_liquidity_aggregates
    except:
        print("could not register in app.config\n\StakeDAO Staked sdCRV")
    return {
        'df_stakedao_sdcrv': sdcrv_base,
        'df_stakedao_sdcrv_known': sdcrv_known,
        'df_stakedao_sdcrv_agg': sdcrv_agg

        # 'df_curve_liquidity_aggregates': df_curve_liquidity_aggregates,
    }