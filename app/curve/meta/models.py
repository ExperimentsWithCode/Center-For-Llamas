from flask import current_app as app

# from ... import db
from app.data.local_storage import (
    pd,
    read_json,
    read_csv,
    write_dataframe_csv,
    write_dfs_to_xlsx
    )


# filename = 'crv_locker_logs'

import ast
from datetime import datetime as dt

from app.utilities.utility import get_period, get_period_end_date
from app.data.reference import (
    known_large_curve_holders,
    gauge_names,
    gauge_symbols,
    current_file_title,
    fallback_file_title,
)
from flask import current_app as app

try:
    # df_curve_locker_history = app.config['df_curve_locker_history']
    # df_gauge_votes_formatted = app.config['df_gauge_votes_formatted']
    df_all_by_gauge = app.config['df_all_by_gauge']
except:
    # from app.curve.gauge_votes.models import df_gauge_votes_formatted
    # from app.curve.locker.models import df_curve_locker_history
    from app.curve.gauge_rounds.models import df_all_by_gauge



print("Loading... { curve.meta.models }")


def generate_round_differences(df, current_round = 0, compare_round=1):
    output = []

    temp = df.sort_values(['period_end_date'], axis = 0, ascending = False)

    period_list = df_all_by_gauge.this_period.unique()
    period_list.sort()

    this_period = period_list[-1 - current_round]
    last_period = period_list[-1 - (current_round + compare_round)]
   

    filter_this_period = temp[
        temp.this_period == this_period
    ]

    filter_last_period = temp[
        temp.this_period == last_period
    ]

    period_end_date_list = df.period_end_date.unique()

    for index, current_row in filter_this_period.iterrows():
        # This Period
        period_end_date = current_row['period_end_date']

        gauge_addr = current_row['gauge_addr']
        name = current_row['name']
        symbol = current_row['symbol']

        total_vote_power = current_row['total_vote_power']
        vote_percent = current_row['vote_percent']
        vecrv_voter_count = current_row['vecrv_voter_count']

        try:
            # -Last Period
            current_row_last_round = filter_last_period[
                filter_last_period.gauge_addr == gauge_addr
            ]
            total_vote_power_1 = current_row_last_round.iloc[0]['total_vote_power']
            vote_percent_1 = current_row_last_round.iloc[0]['vote_percent']
            vecrv_voter_count_1 = current_row_last_round.iloc[0]['vecrv_voter_count']
            period_end_date_1 = current_row_last_round.iloc[0]['period_end_date']
        except:
            total_vote_power_1 = 0
            vote_percent_1  = 0
            vecrv_voter_count_1 = 0
            period_end_date_1 = period_end_date_list[current_round + compare_round]


        output.append({
            'gauge_addr' : gauge_addr,
            'name': name,
            'symbol': symbol,
            'display_name': symbol +" ("+ gauge_addr[0:6] + ")",

            'period': this_period,
            'period_end_date': period_end_date,
            'period_end_date_compared': period_end_date_1,

            'vote_delta':  (vote_percent - vote_percent_1) / vote_percent_1 if vote_percent_1 else 0,
            'vote_percent':  vote_percent,
            'last_vote_percent': vote_percent_1,

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
        'name', 
        'period_end_date', 
        'period_end_date_compared', 
        'power_difference',
        'power_delta', 
        'total_vote_power',
        'last_total_vote_power', 
        'vote_percent',
        'vote_delta', 
        'symbol',
        'display_name'

        ]]

def get_meta(round=0, top_x = 20, compare_round=1):
    output = generate_round_differences(df_all_by_gauge, round, compare_round)
    df_vote_deltas = pd.json_normalize(output)
    df_head, df_tail = generate_head_and_tail(df_vote_deltas, top_x)
    return df_head, df_tail