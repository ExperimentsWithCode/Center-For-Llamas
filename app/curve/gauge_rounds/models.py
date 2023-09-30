
from flask import current_app as app

from datetime import datetime, timedelta
from app.utilities.utility import timed


from app.data.local_storage import (
    pd,
    read_json, 
    read_csv,  
    write_dataframe_csv,
    write_dfs_to_xlsx
    )
from app.utilities.utility import get_period

try:
    df_history_data = app.config['df_history_data']
    df_gauge_votes_formatted = app.config['df_gauge_votes_formatted']

except:
    from app.curve.gauge_votes.models import df_gauge_votes_formatted
    from app.curve.locker.models import df_history_data


print("Loading... { curve.gauge_rounds.models }")

def calc_vote_utilization(current_date, vote_period_date, final_lock_time):
    # four years forward date
    four_years_forward = current_date + timedelta(days=(7 * 52 * 4))
    four_years_forward = four_years_forward.date()

    # Lock time
    local_final_lock_time = final_lock_time.dt.date

    # Vote end
    period_date = vote_period_date

    # Get % of four years lock extends
    ## Calcualted at time of lock and does not update from external activities
    diff_lock_time = local_final_lock_time - period_date
    diff_max_lock = four_years_forward - period_date

    # print(diff_lock_time)
    diff_lock_weeks = diff_lock_time / pd.Timedelta(days=7)
    diff_max_weeks = diff_max_lock / pd.Timedelta(days=7)

    vote_utilization = diff_lock_weeks / diff_max_weeks

    return vote_utilization

# @timed
def generate_aggregation(df_lock_history, df_gauge_votes_formatted):
    dfs = []
    titles = []

    aggregate_dfs = []
    aggregate_titles = []

    max_period = df_lock_history.period.max()
    this_period = df_lock_history.period.min()

    # Go back 10 periods
    i = -0.1

    # print(datetime.now() + timedelta(days=5, hours=-5))
    current_date = datetime(2020, 8, 20)
    current_date = current_date + timedelta(days=7)
    end_date = datetime.now()

    while current_date <= end_date:
        this_period = get_period(0,0, current_date)
        
        # get all votes prior to period
        temp_lock = df_lock_history[df_lock_history['period']<= this_period ]
        temp_vote = df_gauge_votes_formatted[df_gauge_votes_formatted['period'] <= this_period]

        # Filter for most recent vote/lock per user per gauge
        temp_lock = temp_lock.sort_values('timestamp').groupby(['provider']).tail(1000)
        temp_vote = temp_vote.sort_values('time').groupby(['user', 'gauge_addr', 'symbol']).tail(1)

        # combine vote and lock information
        df_combo = pd.merge(temp_vote, temp_lock, how='left', left_on = 'user', right_on = 'provider')
        df_combo["vote_power_raw"] = (
            ( df_combo["weight"]) / 10000 * df_combo["balance_adj"]
        )
        # To only get locks before vote.
        df_combo = df_combo[df_combo['timestamp'] < df_combo['time']]
        df_combo = df_combo.sort_values(['time','timestamp']).groupby(['provider', 'gauge_addr']).tail(1)
        
        # Clear dead weight
        df_combo = df_combo[
            (df_combo['vote_power_raw'] > 0 ) | (df_combo['period_x'] == this_period )
            ]
        df_combo = df_combo[df_combo['final_lock_time'] > current_date + timedelta(days=7)]


        # Set period, handle joining with leading 0s, and cut down decimals.
        df_combo["this_period"] = this_period
        df_combo["period_end_date"] = current_date

        # Calc vote weight decay
        df_combo['vote_utilization'] = (
            calc_vote_utilization(current_date, df_combo['period_end_date_y'], df_combo['final_lock_time'])
            )
        df_combo['vote_power'] = df_combo['vote_power_raw'] * df_combo['vote_utilization']




        this_period_title = str(this_period)
        if len(this_period_title) > 7:
            this_period_title = this_period_title[:7]


        # Update Vote Percent
        df_combo["vote_percent"] = (
            df_combo["vote_power"] / df_combo.vote_power.sum()
        )
        # Update lists
        dfs.append(df_combo)
        titles.append(f"{this_period_title}")

        # Aggregate info down to particular gauges
        df_vote_aggregates = df_combo[[
            'this_period', 'period_end_date','gauge_addr', 'name', 'symbol', 'vote_power', 
            ]].groupby([
                'this_period', 'period_end_date','gauge_addr', 'name', 'symbol',
            ])['vote_power'].agg(['sum','count']).reset_index()
        
        df_vote_aggregates = df_vote_aggregates.rename(columns={
            "sum": 'total_vote_power',
            'count': 'vecrv_voter_count'})
        
        # Update Vote Percent
        df_vote_aggregates["vote_percent"] = (
            (df_vote_aggregates["total_vote_power"] / df_vote_aggregates['total_vote_power'].sum()) * 100
        )
        
        # update aggregate lists
        aggregate_dfs.append(df_vote_aggregates)
        aggregate_titles.append(f"Aggregate: {this_period_title}")

        # update index.
        current_date = current_date + timedelta(days=7)


    return {'dfs': dfs, 
            'titles': titles, 
            'aggregate_dfs': aggregate_dfs, 
            'aggregate_titles': aggregate_titles,
            }

# @timed
def concat_all(df_list, sort_list = ["this_period"]):
    df_concat = None
    first = True
    for df in df_list:
        if first:
            df_concat = df
            first = False
            continue
        df_concat = pd.concat([df_concat, df])
    df_concat = df_concat.sort_values(sort_list, axis = 0, ascending = False)
    return df_concat



# def aggregate_vote_power(df, column_name = 'total_vote_power'):
#     # Aggregate Vote Power per gauge/period
#     x = df_all_by_user[['this_period', 'period_end_date','gauge_addr', 'name', 'symbol', 'vote_power']].groupby([
#         'this_period', 'period_end_date','gauge_addr', 'name', 'symbol',
#     ]).sum('sum').reset_index()
#     return x.rename(columns={"vote_power": column_name,})


# def process_meta(df_all_by_user):
#     # Aggregate Vote Power per gauge/period
#     df_total_vote_power = aggregate_vote_power(df_all_by_user)  
    
#     # Aggregate Vote Count per gauge/period
#     x = df_all_by_user[['this_period', 'period_end_date','gauge_addr', 'name', 'symbol', 'user']].groupby([
#     'this_period', 'period_end_date','gauge_addr', 'name', 'symbol',
#     ]).value_counts('number_of_votes').reset_index()
#     x= x[['this_period', 'period_end_date','gauge_addr', 'name', 'symbol', 'user']].groupby([
#         'this_period', 'period_end_date','gauge_addr', 'name', 'symbol',
#         ]).count().reset_index()
#     df_voter_count = x.rename(columns={"user": "vecrv_voter_count",})

    
#     # Combine Vote Power and Vote Count
#     df_combo = pd.merge(
#         df_total_vote_power, 
#         df_voter_count, 
#         how='left', 
#         left_on = ['this_period', 'period_end_date','gauge_addr', 'name', 'symbol'], 
#         right_on = ['this_period', 'period_end_date','gauge_addr', 'name', 'symbol']
#     )


#     df_combo = df_combo.sort_values(["this_period", 'total_vote_power'], axis = 0, ascending = False)

#     return df_combo


df_book = generate_aggregation(df_history_data, df_gauge_votes_formatted)

df_combo_by_user_list = df_book['dfs']
df_combo_by_gauge_list = df_book['aggregate_dfs']

df_all_by_user = concat_all(df_combo_by_user_list, ['this_period','vote_power' ])
df_all_by_gauge = concat_all(df_combo_by_gauge_list,  ['this_period', 'total_vote_power' ])

df_meta_gauge_aggregate = df_all_by_gauge

try:
    app.config['df_gauge_rounds_all_by_user'] = df_all_by_user
    app.config['df_gauge_rounds_all_by_gauge'] = df_all_by_gauge
    app.config['df_gauge_rounds_aggregate'] = df_all_by_gauge
except:
    print("could not register in app.config\n\tGauge Rounds")

# df_gauge_votes_formatted_temp = df_gauge_votes_formatted[df_gauge_votes_formatted['user']== '0x989aeb4d175e16225e39e87d0d97a3360524ad80']
# convex_out = generate_aggregation(df_history_data, df_gauge_votes_formatted_temp)
# df_combo_by_gauge_list_convex = convex_out['aggregate_dfs'][-1]
