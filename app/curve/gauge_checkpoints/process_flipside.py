from flask import current_app as app
from app.data.reference import filename_curve_gauge_rounds_by_user, filename_curve_gauge_rounds_by_aggregate

from datetime import datetime, timedelta
from app.utilities.utility import timed


from app.data.local_storage import (
    pd,
    read_json, 
    read_csv,  
    write_dataframe_csv,
    write_dfs_to_xlsx
    )
from app.utilities.utility import (
    get_period,
    get_datetime_obj,
    concat_all,
    calc_lock_efficiency_by_checkpoint,
    get_checkpoint_timestamp_from_id,
    concat_all,
)

try:
    df_curve_vecrv = app.config['df_curve_vecrv']
    df_gauge_votes_formatted = app.config['df_gauge_votes_formatted']

except:
    from app.curve.gauge_votes.models import df_gauge_votes_formatted
    from app.curve.locker.models import df_curve_vecrv


def process_checkpoints(df_gauge_votes_formatted, df_curve_vecrv):
    dfs = []
    # aggregate_dfs = []

    for this_checkpoint in df_gauge_votes_formatted.checkpoint_id.unique():
        # get all votes prior to period
        temp_lock = df_curve_vecrv[
            df_curve_vecrv['checkpoint_id'] <= this_checkpoint
            ]
        temp_vote = df_gauge_votes_formatted[
            df_gauge_votes_formatted['checkpoint_id'] <= this_checkpoint
            ]

        # Filter for most recent vote/lock per user per gauge
        filtered_temp_lock = temp_lock.sort_values('checkpoint_timestamp', ascending=True).groupby(
            ['provider']
            ).tail(100)
        filtered_temp_vote = temp_vote.sort_values('time', ascending=True).groupby(
            ['user', 'gauge_addr', 'symbol']
            ).tail(1)

        # combine vote and lock information
        df_combo = pd.merge(
            filtered_temp_vote, 
            filtered_temp_lock, 
            how='left', 
            left_on = 'user', 
            right_on = 'provider')
        
        # To only get locks before vote.
        df_combo = df_combo[df_combo['block_timestamp'] <= df_combo['time']]
        df_combo = df_combo.sort_values(['time','block_timestamp']).groupby(['provider', 'gauge_addr']).tail(1)
        
        # Clear dead weight
        # df_combo = df_combo[
        #     (df_combo['vote_power_raw'] > 0 ) | (df_combo['period_x'] == this_period )
        #     ]
        df_combo = df_combo[df_combo['final_checkpoint_id'] > this_checkpoint]

        # df_combo['final_lock_time']        = df_combo['final_lock_time'].apply(get_date_obj)

        # calc_lock_efficiency_by_checkpoint(this_checkpoint, df)
        # processed_df['balance_delta'] = processed_df.apply(lambda x: self.adjust_withdraws(x), axis=1)

        # get vote power from weight and lock
        df_combo["vote_power_raw"] = (
            ( df_combo["weight"]) / 10000 * df_combo["locked_balance"]
            )
        # df_combo["vote_power"] = (
        #     ( df_combo["weight"]) / 10000 * df_combo["effective_locked_balance"]
        #     )
        # Ensure everything is at most current checkpoint
        df_combo["checkpoint_id"] = this_checkpoint
        """
        THIS RIGHT HERE UPDATE TO REALLY QUERY IT
        """
        df_combo["checkpoint_timestamp"] = get_checkpoint_timestamp_from_id(this_checkpoint)

        df_combo = df_combo.rename(columns={
            'known_as_x': 'known_as',

            'name': 'gauge_name',
            'symbol': 'gauge_symbol',

            'locked_balance': 'locked_crv', 

            'checkpoint_id_x': 'vote_checkpoint_id',
            'checkpoint_timestamp_x': 'vote_checkpoint_timestamp',
            'time': 'vote_timestamp',

            'checkpoint_id_y': 'lock_checkpoint_id',
            'checkpoint_timestamp_y': 'lock_checkpoint_timestamp',
            'block_timestamp': 'lock_timestamp'

            })
    
        df_combo['efficiency'] = df_combo.apply(
            lambda x: calc_lock_efficiency_by_checkpoint(
                x['checkpoint_id'],
                x['final_checkpoint_id']
                ), 
            axis=1
            )
        df_combo['vecrv_balance'] = df_combo['efficiency'] * df_combo['locked_crv']
        df_combo['vote_power'] = df_combo['weight'] / 10000 * df_combo['vecrv_balance']

        # Update Vote Percent
        df_combo["vote_percent"] = (
            df_combo["vote_power"] / df_combo.vote_power.sum()
        )
        
        # Update lists
        dfs.append(df_combo)
    df_concat = concat_all(dfs, ['checkpoint_id', 'vote_power']) 
    df_concat = df_concat[[
        # Checkpoint Info
        'checkpoint_id',
        'checkpoint_timestamp',
        # Voter Info
        'voter',
        'known_as',
        # Gauge Info
        'gauge_addr',
        'gauge_name',
        'gauge_symbol',
        # Vote Info
        'weight',
        'vote_checkpoint_id',
        'vote_checkpoint_timestamp',
        'vote_timestamp',
        # Lock Info
        'locked_crv',
        'lock_checkpoint_id',
        'lock_checkpoint_timestamp',
        'lock_timestamp',
        'final_checkpoint_id',
        'final_checkpoint_timestamp',
        # Derrived Info
        'vecrv_balance',
        'vote_power',
        'vote_percent',
        'efficiency'
    ]]
    return df_concat

def process_checkpoint_aggs(df):
    # Aggregate info down to particular gauges
    df_vote_aggs = df.groupby([
                # 'final_lock_time',
                'checkpoint_timestamp',
                'checkpoint_id',
                'gauge_addr',
                'gauge_name',
                'gauge_symbol',
            ]).agg(
            total_vote_power=pd.NamedAgg(column='vote_power', aggfunc=sum),
            total_raw_vote_power=pd.NamedAgg(column='locked_crv', aggfunc=sum),
            total_vote_percent=pd.NamedAgg(column='vote_percent', aggfunc=sum),

            ).reset_index()
    df_vote_aggs = df_vote_aggs.sort_values(['checkpoint_timestamp', 'total_vote_power'])
    return df_vote_aggs


def process_and_save():
    print("Processing... { curve.gauge_checkpoints.models }")

    df_checkpoints = process_checkpoints(df_gauge_votes_formatted, df_curve_vecrv)
    df_checkpoints_aggs = process_checkpoint_aggs(df_checkpoints)

    write_dataframe_csv(filename_curve_gauge_rounds_by_user, df_checkpoints, 'processed')

    write_dataframe_csv(filename_curve_gauge_rounds_by_aggregate, df_checkpoints_aggs, 'processed')

    try:
        app.config['df_checkpoints'] = df_checkpoints
        app.config['df_checkpoints_aggs'] = df_checkpoints_aggs
    except:
        print("could not register in app.config\n\tGauge Rounds")
    return {
        'df_checkpoints': df_checkpoints,
        'df_checkpoints_aggs': df_checkpoints_aggs
    }

