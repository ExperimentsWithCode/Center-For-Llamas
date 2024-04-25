from flask import current_app as app

# from ... import db
from app.data.local_storage import (
    pd,
    csv_to_df,
    df_to_csv
    )

from app.utilities.utility import (
    format_plotly_figure,
    get_checkpoint_id,
    get_checkpoint_timestamp_from_id,
    convert_units,
    print_mode
)


# filename = 'crv_locker_logs'

import ast
from datetime import datetime as dt

# from app.utilities.utility import get_period, get_checkpoint_timestamp
from app.data.reference import (
    known_large_market_actors,
    gauge_names,
    gauge_symbols,
    current_file_title,
    fallback_file_title,
)
from flask import current_app as app

try:
    # df_curve_locker_history = app.config['df_curve_locker_history']
    # df_gauge_votes_formatted = app.config['df_gauge_votes_formatted']
    df_checkpoints_agg = app.config['df_checkpoints_agg']
    df_votium_v2 = app.config['df_votium_v2']
    df_curve_liquidity_aggregates = app.config['df_curve_liquidity_aggregates']
    # df_curve_liquidity = app.config['df_curve_liquidity']
    df_curve_oracles_agg = app.config['df_curve_oracles_agg']

except:
    # from app.curve.gauge_votes.models import df_gauge_votes_formatted
    # from app.curve.locker.models import df_curve_locker_history
    from app.curve.gauge_checkpoints.models import df_checkpoints_agg
    from app.convex.votium_bounties_v2.models import df_votium_v2
    from app.curve.liquidity.models import df_curve_liquidity_aggregates
    from app.curve.liquidity.models import df_curve_oracles_agg



 
    print_mode("Loading... { curve.meta.models }")


def generate_round_differences(df, current_round = 0, compare_round=1):
    output = []

    temp = df.sort_values(['checkpoint_timestamp'], axis = 0, ascending = False)

    checkpoint_id_list = df_checkpoints_agg.checkpoint_id.unique()
    checkpoint_id_list.sort()

    checkpoint_id = checkpoint_id_list[-1 - current_round]
    last_checkpoint_id = checkpoint_id_list[-1 - (current_round + compare_round)]
   

    filter_checkpoint_id = temp[
        temp.checkpoint_id == checkpoint_id
    ]

    filter_last_checkpoint_id = temp[
        temp.checkpoint_id == last_checkpoint_id
    ]

    checkpoint_timestamp_list = df.checkpoint_timestamp.unique()

    for index, current_row in filter_checkpoint_id.iterrows():
        # This Period
        checkpoint_timestamp = current_row['checkpoint_timestamp']

        gauge_addr = current_row['gauge_addr']
        name = current_row['gauge_name']
        symbol = current_row['gauge_symbol']

        total_vote_power = current_row['total_vote_power']
        vote_percent = current_row['total_vote_percent']
        # vecrv_voter_count = current_row['vecrv_voter_count']

        try:
            # -Last Period
            current_row_last_round = filter_last_checkpoint_id[
                filter_last_checkpoint_id.gauge_addr == gauge_addr
            ]
            total_vote_power_1 = current_row_last_round.iloc[0]['total_vote_power']
            vote_percent_1 = current_row_last_round.iloc[0]['total_vote_percent']
            # vecrv_voter_count_1 = current_row_last_round.iloc[0]['vecrv_voter_count']
            checkpoint_timestamp_1 = current_row_last_round.iloc[0]['checkpoint_timestamp']
        except:
            total_vote_power_1 = 0
            vote_percent_1  = 0
            vecrv_voter_count_1 = 0
            checkpoint_timestamp_1 = checkpoint_timestamp_list[-1 - (current_round + compare_round)]


        output.append({
            'gauge_addr' : gauge_addr,
            'gauge_name': name,
            'gauge_symbol': symbol,
            'display_name': symbol +" ("+ gauge_addr[0:6] + ")",

            'checkpoint_id': checkpoint_id,
            'checkpoint_timestamp': checkpoint_timestamp,
            'checkpoint_timestamp_compared': checkpoint_timestamp_1,

            'vote_delta':  (vote_percent - vote_percent_1) / vote_percent_1 if vote_percent_1 else 0,
            'total_vote_percent':  vote_percent,
            'last_total_vote_percent': vote_percent_1,

            'power_delta': total_vote_power /  total_vote_power_1  if total_vote_power_1 else 0,
            'total_vote_power': total_vote_power,
            'last_total_vote_power': total_vote_power_1,
            'power_difference': total_vote_power -  total_vote_power_1,
            
        })
    return output


def generate_head_and_tail(df, top_x = 20):

    local_df_vote_deltas = df.sort_values(['power_difference'], axis = 0, ascending = False)

    local_df_vote_deltas_head = local_df_vote_deltas.head(top_x)
    local_df_vote_deltas_tail = local_df_vote_deltas.tail(top_x)

    df_vote_deltas_head_formatted = _format_df(local_df_vote_deltas_head)
    df_vote_deltas_tail_formatted = _format_df(local_df_vote_deltas_tail)

    return df_vote_deltas_head_formatted, df_vote_deltas_tail_formatted


def _format_df(df):
    return df[
        ['gauge_addr', 
        'gauge_name', 
        'checkpoint_timestamp', 
        'checkpoint_timestamp_compared', 
        'power_difference',
        'power_delta', 
        'total_vote_power',
        'last_total_vote_power', 
        'total_vote_percent',
        'vote_delta', 
        'gauge_symbol',
        'display_name'

        ]]

def get_meta(round=0, top_x = 20, compare_round=1):
    output = generate_round_differences(df_checkpoints_agg, round, compare_round)
    df_vote_deltas = pd.json_normalize(output)
    df_head, df_tail = generate_head_and_tail(df_vote_deltas, top_x)
    return df_head, df_tail




class ProcessContributingFactors():
    def __init__(self):
        pass

    def process_all(self, target_gauge, compare_back):
        df0 = self.process(target_gauge, compare_back)
        df1 = self.process_issuance(df0)
        df2 = self.process_oracle(df1)
        return df2.sort_values(['checkpoint_timestamp', 'issuance_value'], ascending=False)

    def process(self, target_gauge, compare_back):
        if type(target_gauge) == str:
            target_gauge = [target_gauge]
        df_checkpoints_local = df_checkpoints_agg[df_checkpoints_agg['gauge_addr'].isin(target_gauge)]
        df_checkpoints_local = df_checkpoints_local[df_checkpoints_local['checkpoint_id'] > df_checkpoints_local.checkpoint_id.max() - compare_back]
        
        df_votium_v2_local = df_votium_v2[df_votium_v2['gauge_addr'].isin(target_gauge)]
        df_votium_v2_local = df_votium_v2_local[df_votium_v2_local['checkpoint_id'] > df_votium_v2_local.checkpoint_id.max() - compare_back]

        df_curve_liquidity_local = df_curve_liquidity_aggregates[df_curve_liquidity_aggregates['gauge_addr'].isin(target_gauge)]
        df_curve_liquidity_local = df_curve_liquidity_local[df_curve_liquidity_local['checkpoint_id'] > df_curve_liquidity_local.checkpoint_id.max() - compare_back]

        df_checkpoints_local = df_checkpoints_local[[
            'checkpoint_id',
            'checkpoint_timestamp',
            'gauge_addr',
            'gauge_name',
            'gauge_symbol',
            'total_vote_power',
            'total_vote_percent'
            ]]
        
        df_votium_v2_local = df_votium_v2_local[[
            'bounty_amount',
            'bounty_value',
            # 'price',
            # 'depositor',
            # 'excluded',
            'gauge_addr',
            'votium_round',
            'token',
            'token_name',
            'token_symbol',
            'checkpoint_id',
            # 'total_vote_power',
            # 'total_vote_percent',
            # 'total_bounty_value',
            'relative_vote_power',
            'bounty_per_vecrv',
            'bounty_per_vecrv_percent',
            'vecrv_per_bounty',
            'vecrv_percent_per_bounty'
            ]].sort_values(['checkpoint_id', 'token_symbol', ])

        df_votium_v2_local = df_votium_v2_local.groupby([
            'checkpoint_id',
            'votium_round',
            # 'total_vote_percent',
            # 'total_vote_power',
            # 'total_bounty_value',
            # 'gauge_name',
            'gauge_addr',
            # 'total_vote_power'
            ]).agg(
            total_bounty_value=pd.NamedAgg(column='bounty_value', aggfunc='sum'),
            bounty_values=pd.NamedAgg(column='bounty_value', aggfunc=list),
            bounty_tokens=pd.NamedAgg(column='token_symbol', aggfunc=list),
            bounty_amounts=pd.NamedAgg(column='bounty_amount', aggfunc=list),

            ).reset_index()



        df_curve_liquidity_local['tradable_assets'] = df_curve_liquidity_local['tradable_assets'].apply(self.format_list)

        df_curve_liquidity_local = df_curve_liquidity_local.groupby([
                # 'final_lock_time',
            'checkpoint_id',
            'gauge_addr',
            # 'total_vote_power',
            'tradable_assets',
            ]).agg(
            total_balance=pd.NamedAgg(column='total_balance', aggfunc='mean'),
            total_balance_usd=pd.NamedAgg(column='total_balance_usd', aggfunc='mean'),
            liquidity_over_votes=pd.NamedAgg(column='liquidity_over_votes', aggfunc='mean'),
            liquidity_usd_over_votes=pd.NamedAgg(column='liquidity_usd_over_votes', aggfunc='mean'),

            ).reset_index()
            
        df_combo = pd.merge(
            df_checkpoints_local, 
            df_votium_v2_local, 
            how='left', 
            on = ['checkpoint_id', 'gauge_addr'], 
            )

        df_combo[['votium_round']] = df_combo[['votium_round']].ffill()
            
        df_combo = pd.merge(
            df_combo, 
            df_curve_liquidity_local, 
            how='left', 
            on = ['checkpoint_id', 'gauge_addr'], 
            )
        
        return df_combo

    def format_list(self, string_in):
        out = []
        try:
            for n in string_in.split(','):
                n2 = n.strip().strip('[').strip(']')
                # print(n2)
                out.append(n2)
            out.sort()
        except:
            print_mode(string_in)
        return str(out).replace("'", "")

    def generate_issuance_map(self, annual_issuance):
        i = 1
        issuance_map = {}
        while i < 52*6:
            issuance_rate_id = int(i/52)
            annual_crv = annual_issuance[issuance_rate_id]
            issuance_map[i] = annual_crv / 52
            i+= 1
        return issuance_map
    
    def apply_issuance(self, row, weekly_issuance_map):
        # try:
        #     int(row['checkpoint_id'])
        # except:
        #     return 0
        if row['checkpoint_id'] in weekly_issuance_map and 'total_vote_percent' in row:
            return weekly_issuance_map[row['checkpoint_id']] * row['total_vote_percent']
        else:
            return 0
        # except Exception as e:
        #     print(e)
        #     print(row['checkpoint_id'])
        #     print(row['total_vote_percent'])
        #     print(weekly_issuance_map[row['checkpoint_id']])

    def process_issuance(self, df):
        annual_issuance = [
            194323750.00,
            163406144.00,
            137407641.00,
            115545593.00,
            97161875.00,
            81703072.50,
        ]
        weekly_issuance_map = self.generate_issuance_map(annual_issuance)

        df['issuance_distributed'] = df.apply(lambda x: self.apply_issuance(x, weekly_issuance_map), axis=1)
        return df

    def get_adjusted_checkpoint_id(self, x):
        return get_checkpoint_id(x) - 1

    def get_oracle_checkpoint_aggs(self, df):
        df = df.copy()

        df['checkpoint_id'] = df['block_timestamp'].apply(self.get_adjusted_checkpoint_id)
        df['checkpoint_timestamp'] = df['checkpoint_id'].apply(get_checkpoint_timestamp_from_id)
        processed_agg = df[['checkpoint_id', 'calc_price']].groupby([
            'checkpoint_id',
            ]).agg(
            avg_crv_price=pd.NamedAgg(column='calc_price', aggfunc='mean')).reset_index()
        return processed_agg

    def process_oracle(self, df):
        df_crv_oracle = df_curve_oracles_agg[df_curve_oracles_agg['token_addr'] == '0xd533a949740bb3306d119cc777fa900ba034cd52']

        df_checkpoint_oracle = self.get_oracle_checkpoint_aggs(df_crv_oracle)
        df_oracle_combo = pd.merge(
            df, 
            df_checkpoint_oracle, 
            how='left', 
            on = ['checkpoint_id'], 
            )
        
        df_oracle_combo['issuance_value'] = df_oracle_combo['issuance_distributed'] * df_oracle_combo['avg_crv_price']
        # df_oracle_combo['relative_issuance'] = df_oracle_combo['issuance_value'] * df_oracle_combo['bounty_value'] / df_oracle_combo['total_bounty_value']
        # df_oracle_combo['relative_issuance_value'] = df_oracle_combo['relative_issuance'] * df_oracle_combo['avg_crv_price']

        df_oracle_combo['yield_rate'] = (df_oracle_combo['issuance_value'] * 52) / df_oracle_combo['total_balance_usd']
        df_oracle_combo['yield_rate_adj'] = df_oracle_combo['yield_rate'] * 100
        return df_oracle_combo