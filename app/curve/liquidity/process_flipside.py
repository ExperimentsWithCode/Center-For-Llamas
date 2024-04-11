from flask import current_app as app
from app.data.reference import filename_curve_liquidity, filename_curve_liquidity_aggregate, filename_curve_liquidity_swaps, filename_curve_liquidity_oracle_aggregate

from datetime import datetime as dt
from datetime import datetime, timedelta
import numpy as np

import traceback


from app.data.local_storage import (
    pd,
    read_json, 
    read_csv,  
    write_dataframe_csv,
    write_dfs_to_xlsx
    )
from app.utilities.utility import (
    get_checkpoint_id,
    get_checkpoint_timestamp_from_date,
    df_default_checkpoints,
    concat_all,
    utc,
    timed
)

try:
    gauge_registry = app.config['gauge_registry']
    df_checkpoints_agg = app.config['df_checkpoints_agg']

except:
    from app.curve.gauges.models import gauge_registry
    from app.curve.gauge_checkpoints.models import df_checkpoints_agg

class Oracle():
    def __init__(self, df_liquidity):
        self.df_liquidity = self.format_input(df_liquidity)
        self.df_exchanges = self.process_exchange_rates()
        self.df_oracles = self.process_oracle()
        self.df_oracles_agg = self.resample_aggregates()

    @timed
    def format_input(self, df):
        df['amount'] = df.apply(
                lambda x: self.nullify_amount(x['amount']), 
                axis=1)
        # nulify amount sets price to 0 if null
        df['price'] = df.apply(
                lambda x: self.nullify_amount(x['price']), 
                axis=1)
        df['block_timestamp'] = pd.to_datetime(df['block_timestamp'])
        df = self.flush_shitcoins(df)
        return df
    
    def nullify_amount(self, value):
        if value == 'null' or value == '' or value == '-':
            return np.nan
        return float(value)
    """
    Break Out Exchange Rates
    """
    # Isolates swaps and derrives exchange rates
    def process_exchange_rates(self):
        target_list = ['pool_addr', 'tx_hash']
        df = self.get_likely_swaps(self.df_liquidity, target_list)
        df = self.split_pricing(df, target_list)
        df = self.reduce_exchange_rates(df)
        return df
    
    # Clear out tokens that appear to be spam  
    @timed
    def flush_shitcoins(self, df):
        df_counts = df.groupby(['pool_addr', 'token_addr']).size().reset_index(name='counts')
        df_combo_counts = pd.merge(
            df, 
            df_counts, 
            how='left', 
            on = ['pool_addr', 'token_addr' ], 
            )
        df_combo_counts = df_combo_counts[df_combo_counts['counts'] > 3]    # Magic is here
        df_combo_counts = df_combo_counts.drop(['counts'], axis=1)
        return df_combo_counts

    @timed
    def get_counts(self, df, target_list, count_name="counts"):
        df_counts = df.groupby(target_list).size().reset_index(name=count_name)
        df_combo_counts = pd.merge(
            df, 
            df_counts, 
            how='left', 
            on = target_list, 
            )
        return df_combo_counts

    # isolate tx hash with two transfers
    @timed
    def get_likely_swaps(self, df, target_list):
        # Split into tx hash w/ 2 transfers to identify potential swaps
        df = self.get_counts(df, target_list)
        df = df[df['counts'] == 2]
        # Convert values types
        return df

    # isolate likely swaps where 
    #   one token transfers in, the other transfers out
    @timed
    def split_pricing(self, df, target_list):
        # Identifies inner joins where one token transfers in, the other transfers out
        df_combo_positive = df[df['amount'] > 0 ]
        df_combo_negative = df[df['amount'] < 0 ]
        df_oracle = pd.merge(
            df_combo_positive, 
            df_combo_negative, 
            how='inner', 
            on = target_list, 
            )
        
        # Calc exchange rate based on this
        df_oracle['exchange_rate_x_over_y'] = abs(df_oracle['amount_x'] / df_oracle['amount_y'])
        df_oracle['exchange_rate_y_over_x'] = abs(df_oracle['amount_y'] / df_oracle['amount_x'])

        return df_oracle


    # deals with fallout of all the merges
    @timed
    def reduce_exchange_rates(self, df):
        df_x = df[[
            'block_timestamp_x',
            'symbol_x',
            'token_addr_x',
            'symbol_y',
            'token_addr_y',
            'has_price_x',
            'price_x',
            'price_y',
            'exchange_rate_y_over_x' ,
            # 'calc_price_x'
            ]]
        df_y = df[[
            'block_timestamp_x',
            'symbol_y',
            'token_addr_y',
            'symbol_x',
            'token_addr_x',
            'has_price_y',
            'price_y',
            'price_x',
            'exchange_rate_x_over_y' ,
            # 'calc_price_y'
            ]]

        df_x = df_x.rename(columns={
            "block_timestamp_x": 'block_timestamp',
            "symbol_x": 'symbol',
            'token_addr_x': 'token_addr',
            "symbol_y": 'comp_symbol',
            'token_addr_y': 'comp_token_addr',
            "has_price_x": 'has_price',
            'price_x': 'price',
            'price_y': 'comp_price',
            'exchange_rate_y_over_x': 'exchange_rate',
            # 'calc_price_x': 'calc_price'           
            })
        df_y = df_y.rename(columns={
            "block_timestamp_x": 'block_timestamp',
            "symbol_y": 'symbol',
            'token_addr_y': 'token_addr',
            "symbol_x": 'comp_symbol',
            'token_addr_x': 'comp_token_addr',
            "has_price_y": 'has_price',
            'price_y': 'price',
            'price_x': 'comp_price',

            'exchange_rate_x_over_y': 'exchange_rate',
            # 'calc_price_y': 'calc_price'           
            })
        return concat_all([df_x, df_y],['block_timestamp'])

      # Derrives price from exchange rate and comp price
    
    """
    Derrive Pricing
    """
    def process_oracle(self):
        df = self.resample_micro(self.df_exchanges)
        df = self.resample_macro(df)
        return df
    
    def calc_price(self, row):
       # If price, use price
        if np.isnan(row[f"price"]):
            # if no price on b, can't calc a price
            if np.isnan(row[f"comp_price"]):
                return np.nan 
            # else calc price of A off exchange price and b
            return abs( row['exchange_rate'] * row["comp_price"] )
        return row[f"price"]
      
    # resample prices and exchange rates
    @timed
    def resample_micro(self, df):
        df2 = df.set_index(['block_timestamp'])
        # Pricing
        df_prices = df2.groupby(
            ['symbol', 'token_addr', 'comp_symbol', 'comp_token_addr']
            ).resample('1D')['price'].mean().reset_index()
        df_prices
        # reduce
        df_prices = df_prices.dropna()
        df_prices_reduced = df_prices[['symbol', 'token_addr', 'block_timestamp', 'price']]
        # resample exchange rates 
        df_exchange_rates = df2.groupby(
            ['symbol', 'token_addr', 'comp_symbol', 'comp_token_addr']
            ).resample('1D')['exchange_rate'].mean().ffill().reset_index()
        df_exchange_rates
        # Rename for merging comps
        df_prices_reduced_comp = df_prices_reduced.rename(columns={
            "token_addr": 'comp_token_addr',
            "symbol": 'comp_symbol',
            "price": 'comp_price',     
            })
        # Merge
        df_combo_oracle_mid = pd.merge(
            df_exchange_rates, 
            df_prices_reduced_comp, 
            how='left', 
            on = ['block_timestamp', 'comp_symbol', 'comp_token_addr'  ], 
            )
        df_combo_oracle = pd.merge(
            df_combo_oracle_mid, 
            df_prices_reduced, 
            how='left', 
            on = ['block_timestamp', 'symbol', 'token_addr'  ], 
            )
        return df_combo_oracle
    # calc pricing 
    @timed
    def resample_macro(self, df):
        # Reduce Oracle
        df2 = df.set_index(['block_timestamp'])
        df_combo_oracle_reduced = df2.groupby(
            ['symbol', 'token_addr', 'comp_symbol', 'comp_token_addr']
            ).resample('1D')['exchange_rate', 'price', 'comp_price'].mean().reset_index()
        # Calc Price
        df_combo_oracle_reduced['calc_price'] = df_combo_oracle_reduced.apply(
                lambda x: self.calc_price(x),
        axis=1)
        return df_combo_oracle_reduced
    # reduce to single price
    @timed
    def resample_aggregates(self):
        # Reduce Oracle
        df2 = self.df_oracles.set_index(['block_timestamp'])
        df_aggregate_pricing = df2.groupby(
            ['symbol', 'token_addr', ]
            ).resample('1D')['calc_price'].mean().reset_index()
        return df_aggregate_pricing

class Liquidity():
    def __init__(self, df_liquidity, df_checkpoints_agg, gauge_registry):
        self.oracle = Oracle(df_liquidity)
        self.df_liquidity = self.oracle.df_liquidity
        # External Reference
        self.df_checkpoints_agg = df_checkpoints_agg
        self.gauge_registry = gauge_registry
        self.df_processed_liquidity = self.process_liquidity()

    def process_liquidity(self):
        df = self.prime_context()
        df = self.merge_pricing(df)
        df = self.merge_checkpoints(df)
        df = self.process_liquidity_over_votes(df)
        df = df.sort_values(['block_timestamp', 'checkpoint_id', 'balance_usd'], ascending=True)
        return df


    # def estimate_checkpoint(self, min_checkpoint_timestamp, target_timestamp):
    #     diff = target_timestamp - min_checkpoint_timestamp
    #     return round(diff.days/7)

    # Prep w/ gauge/checkpoint info
    @timed
    def prime_context(self):
        # resample
        df2 = self.df_liquidity.set_index(['block_timestamp'])
        df = df2.groupby(
            ['pool_addr', 'symbol', 'token_addr']
            ).resample('1D')['amount'].sum().ffill().reset_index()

        # Calc a cumulative balance to interact w/ price
        df = df.sort_values(['block_timestamp'], ascending=True)
        df['balance'] = df.groupby(['pool_addr', 'symbol', 'token_addr'])['amount'].transform(pd.Series.cumsum)
        df = df[df['balance'] > 0]
        # additive
        df['checkpoint_id'] = df.apply(
            lambda x: get_checkpoint_id(x['block_timestamp']), 
            axis=1)
        
        df['gauge_addr'] = df.apply(
            lambda x: self.gauge_registry.get_gauge_addr_from_pool(x['pool_addr']), 
            axis=1)

        df['gauge_source'] = df.apply(
            lambda x: self.gauge_registry.get_gauge_source_from_pool(x['pool_addr']), 
            axis=1)
        

        return df
    
    #Combine liquidity and checkpoint data
    @timed
    def merge_checkpoints(self, df):
        df_combo = pd.merge(
            df, 
            self.df_checkpoints_agg, 
            how='left', 
            on = ['checkpoint_id', 'gauge_addr' ], 
            )
        return df_combo

    @timed
    def merge_pricing(self, df):
        # Merge price and balance data
        df_combo = pd.merge(
            df, 
            self.oracle.df_oracles_agg, 
            how='left', 
            on = ['block_timestamp', 'symbol', 'token_addr' ], 
            )
        print(df_combo.keys())
        # calc USD priced balance
        df_combo['balance_usd'] = df_combo.apply(
            lambda x: self.calc_amount_usd(x), 
            axis=1)
        return df_combo

    def calc_amount_usd(self, row):
        if np.isnan(row['calc_price']):
            return np.nan
        return row['balance'] * row['calc_price']

    @timed
    def process_liquidity_over_votes(self, df):
        # df
        df['liquidity_over_votes'] = df['balance'] / df['total_vote_power']
        df['liquidity_usd_over_votes'] = df['balance_usd'] / df['total_vote_power']
        return df
     

def get_curve_liquidity_df():
    filename = filename_curve_liquidity    #+ fallback_file_title
    resp_dict = read_csv(filename, 'source') # joined with 
    df_liquidity_source = pd.json_normalize(resp_dict)
    try:
        df_liquidity_source = df_liquidity_source.sort_values("block_timestamp", axis = 0, ascending = True)
    except:
        df_liquidity_source = df_liquidity_source.sort_values("BLOCK_TIMESTAMP", axis = 0, ascending = True)
    return df_liquidity_source

def process_checkpoint_aggs(df):
    df = df[df['balance']> 0]
    # Aggregate info down to particular gauges
    df_aggs = df.groupby([
                # 'final_lock_time',
                'checkpoint_timestamp',
                'checkpoint_id',
                'block_timestamp',
                'gauge_addr',
                'gauge_name',
                'gauge_symbol',
                'pool_addr',
            ]).agg(
            total_vote_power=pd.NamedAgg(column='total_vote_power', aggfunc='mean'),
            total_balance=pd.NamedAgg(column='balance', aggfunc=sum),
            total_balance_usd=pd.NamedAgg(column='balance_usd', aggfunc=sum),
            tradable_assets=pd.NamedAgg(column='symbol', aggfunc=list),
            ).reset_index()
    df_aggs['liquidity_over_votes'] = df_aggs['total_balance'] / df_aggs['total_vote_power']
    df_aggs['liquidity_usd_over_votes'] = df_aggs['total_balance_usd'] / df_aggs['total_vote_power']
    df_aggs = df_aggs.sort_values(['block_timestamp', 'total_vote_power'])
    return df_aggs

def process_and_save():
    try:
    from config import activate_print_mode
except:
    activate_print_mode = False

if activate_print_mode:
    print("Processing... { curve.liquidity.models }")
    liquidity = Liquidity(get_curve_liquidity_df(), df_checkpoints_agg, gauge_registry)

    df_curve_liquidity = liquidity.df_processed_liquidity
    df_curve_liquidity_aggregates = process_checkpoint_aggs(df_curve_liquidity)

    df_curve_swaps = liquidity.oracle.df_exchanges
    df_curve_oracles_agg = liquidity.oracle.df_oracles_agg

    write_dataframe_csv(filename_curve_liquidity, df_curve_liquidity, 'processed')
    write_dataframe_csv(filename_curve_liquidity_aggregate, df_curve_liquidity_aggregates, 'processed')
    write_dataframe_csv(filename_curve_liquidity_swaps, df_curve_liquidity, 'processed')
    write_dataframe_csv(filename_curve_liquidity_oracle_aggregate, df_curve_oracles_agg, 'processed')
    try:
        # app.config['df_active_votes'] = df_active_votes
        app.config['df_curve_liquidity'] = df_curve_liquidity
        app.config['df_curve_liquidity_aggregates'] = df_curve_liquidity_aggregates
        app.config['df_curve_swaps'] = df_curve_swaps
        app.config['df_curve_oracles_agg'] = df_curve_oracles_agg

    except:
        print("could not register in app.config\n\tGauge Liquidity")
    return {
        # 'df_active_votes': df_active_votes,
        'df_curve_liquidity': df_curve_liquidity,
        'df_curve_liquidity_aggregates': df_curve_liquidity_aggregates,
        'df_curve_swaps': df_curve_swaps,
        'df_curve_oracles_agg': df_curve_oracles_agg,
    }


    # all_votes, active_votes = vr.format_active_output()
    # # df_active_votes = pd.json_normalize(active_votes)
    # df_all_votes = pd.json_normalize(all_votes)
    # write_dataframe_csv(filename_curve_gauge_votes_all, df_all_votes, 'processed')

    # df_gauge_votes_formatted = get_votes_formatted(vr)
    # write_dataframe_csv(filename_curve_gauge_votes_formatted, df_gauge_votes_formatted, 'processed')

    # df_current_gauge_votes = get_current_votes(df_gauge_votes_formatted)
    # write_dataframe_csv(filename_curve_gauge_votes_current, df_current_gauge_votes, 'processed')

    # try:
    #     # app.config['df_active_votes'] = df_active_votes
    #     app.config['df_all_votes'] = df_all_votes
    #     app.config['df_gauge_votes_formatted'] = df_gauge_votes_formatted
    #     app.config['df_current_gauge_votes'] = df_current_gauge_votes
    # except:
    #     print("could not register in app.config\n\tGauge Votes")
    # return {
    #     # 'df_active_votes': df_active_votes,
    #     'df_all_votes': df_all_votes,
    #     'df_gauge_votes_formatted': df_gauge_votes_formatted,
    #     'df_current_gauge_votes': df_current_gauge_votes
    # }


