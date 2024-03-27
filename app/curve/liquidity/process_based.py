from flask import current_app as app

from app.data.local_storage import (
    pd,
    read_json, 
    read_csv,  
    write_dataframe_csv,
    write_dfs_to_xlsx
    )

from app.utilities.utility import (
    concat_all
)


class ProcessBasedLiquidity():
    def __init__(self, df_curve_gauge_registry, df_curve_liquidity):
        self.df_gauges = df_curve_gauge_registry
        self.df_liquidity = df_curve_liquidity
        self.df_based_liquidity = None
        self.df_based_leftovers = None
        self.df_base_pools = None
        self.df_rebased_liquidity = None
        self.merge_set()

    def split_liquidity(self, is_rebase = False) :
        df_base = self.df_rebased_liquidity if is_rebase else self.df_liquidity

        pool_addr_list = self.df_gauges.pool_addr.unique()
        # LPs w/ Base Pools
        self.df_based_liquidity = df_base[df_base['token_addr'].isin(pool_addr_list)]
        # Remaining assets in LPs w/ Base Pools
        leftovers_temp = df_base[
            df_base['pool_addr'].isin(self.df_based_liquidity.pool_addr.unique())
            ]
        self.df_based_leftovers = leftovers_temp[
            ~leftovers_temp['token_addr'].isin(pool_addr_list)
            ]
        # Base Pools
        self.df_base_pools = df_base[
            df_base['pool_addr'].isin(self.df_based_liquidity .token_addr.unique())
            ]

    def merge_match(self):
        self.merge_set()
        # Rebase for base pools with a basepool
        self.merge_set()
        # Join with non base pool liquidity
        self.df_rebased_liquidity = self.merge_leftovers()

    def merge_set(self, is_rebase = False):
        self.split_liquidity(is_rebase)
        # Rebase
        self.df_rebased_liquidity = self.merge_base()


    def merge_base(self):
        # df_base = self.df_rebased_liquidity if is_rebase else self.df_based_liquidity
        # Combine base pools with lp's with base pools
        df = pd.merge(
            self.df_based_liquidity,
            self.df_base_pools,
            how='left',
            left_on=['checkpoint_timestamp', 'checkpoint_id', 'block_timestamp', 'token_addr'],
            right_on=['checkpoint_timestamp', 'checkpoint_id', 'block_timestamp', 'pool_addr']
        )
        # Sum base pool balances
        df = self.merge_aggregate_sum(df)

        # W/ sum, calculate balance of pool
        df['percent_y_usd'] = df['balance_usd_y'] / df['sum_usd_y']
        df['based_balance_usd'] = df['percent_y_usd'] * df['balance_usd_x']
        df['based_balance'] = df['based_balance_usd'] / df['calc_price_y']

        df = self.reset(df)
        return df

    
    def merge_aggregate_sum(self, df):
        df_aggs = df.groupby([
            'checkpoint_timestamp',
            'checkpoint_id', 
            'pool_addr_x',
            'token_addr_x',
            ]).agg(
                sum_usd_y=pd.NamedAgg(column='balance_usd_y', aggfunc='sum'),
                sum_y_=pd.NamedAgg(column='balance_y', aggfunc='sum'),

                ).reset_index()
        df = pd.merge(
            df,
            df_aggs,
            how='left',
            left_on=['checkpoint_timestamp', 'checkpoint_id', 'pool_addr_x', 'token_addr_x'],
            right_on=['checkpoint_timestamp', 'checkpoint_id', 'pool_addr_x', 'token_addr_x']
            )
        return df
    
    def reset(self, df):
        df = df[[
            'checkpoint_id',
            'checkpoint_timestamp',
            'block_timestamp',
            'gauge_addr_x',
            'gauge_name_x',
            'gauge_source_x',
            'gauge_symbol_x',
            'pool_addr_x',
            'symbol_y',
            'token_addr_y',
            'amount_y',
            'based_balance_usd',
            'based_balance',
            'calc_price_y',
            # 'liquidity_over_votes_y',
            # 'liquidity_usd_over_votes_y',
            'total_raw_vote_power_y',
            'total_vote_percent_y',
            'total_vote_power_y',
            ]]
        
        df = df.rename(columns={
            'checkpoint_id': 'checkpoint_id',
            'checkpoint_timestamp': 'checkpoint_timestamp',

            # 'block_timestamp_x': 'block_timestamp_x',
            'block_timestamp': 'block_timestamp',

            'gauge_addr_x': 'gauge_addr',
            'gauge_name_x': 'gauge_name',
            'gauge_source_x': 'gauge_source',
            'gauge_symbol_x': 'gauge_symbol',
            'pool_addr_x': 'pool_addr',

            # 'gauge_addr_y': 'gauge_addr',
            # 'gauge_name_y': 'gauge_name',
            # 'gauge_source_y': 'gauge_source',
            # 'gauge_symbol_y': 'gauge_symbol',
            # 'pool_addr_y': 'pool_addr',

            # 'symbol_x': 'symbol_x',
            # 'token_addr_x': 'token_addr_x',
            # 'amount_x': 'amount_x',
            # 'balance_usd_x': 'balance_usd_x',
            # 'balance_x': 'balance_x',
            # 'calc_price_x': 'calc_price_x',
            # 'liquidity_over_votes_x': 'liquidity_over_votes_x',
            # 'liquidity_usd_over_votes_x': 'liquidity_usd_over_votes_x',
            # 'total_raw_vote_power_x': 'total_raw_vote_power_x',
            # 'total_vote_percent_x': 'total_vote_percent_x',
            # 'total_vote_power_x': 'total_vote_power_x',

            'symbol_y': 'symbol',
            'token_addr_y': 'token_addr',
            'amount_y': 'amount',
            'based_balance_usd': 'balance_usd',
            'based_balance': 'balance',
            'calc_price_y': 'calc_price',
            # 'liquidity_over_votes_y': 'liquidity_over_votes',
            # 'liquidity_usd_over_votes_y': 'liquidity_usd_over_votes',
            'total_raw_vote_power_y': 'total_raw_vote_power',
            'total_vote_percent_y': 'total_vote_percent',
            'total_vote_power_y': 'total_vote_power',

            # 'sum_usd_y': 'sum_usd_y',
            # 'sum_y_': 'sum_y_',
            # 'percent_y_usd': 'percent_y_usd',
            })
        df['liquidity_over_votes'] = df['balance'] / df['total_vote_power']
        df['liquidity_usd_over_votes'] = df['balance_usd'] / df['total_vote_power']

        return df

    def merge_leftovers(self):
        return concat_all([self.df_rebased_liquidity, self.df_based_leftovers], ['checkpoint_id', 'block_timestamp'])

