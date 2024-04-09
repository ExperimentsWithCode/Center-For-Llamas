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
except:
    # from app.curve.gauge_votes.models import df_gauge_votes_formatted
    # from app.curve.locker.models import df_curve_locker_history
    from app.curve.gauge_checkpoints.models import df_checkpoints_agg



print("Loading... { curve.meta.models }")


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