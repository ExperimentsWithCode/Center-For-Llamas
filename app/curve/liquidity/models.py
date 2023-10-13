import traceback


try:
    from flask import current_app as app
except:
    pass

from app.data.local_storage import (
    pd,
    read_json,
    read_csv,
    write_dataframe_csv,
    write_dfs_to_xlsx
    )

from app.utilities.utility import timed

import ast
from datetime import datetime as dt
from datetime import timedelta




try:
    df_all_by_gauge = app.config['df_all_by_gauge']
    gauge_registry = app.config['gauge_registry']

except:
    from app.curve.gauge_rounds.models import df_all_by_gauge
    from app.curve.gauges.models import gauge_registry

    # from app.curve.locker.models import df_history_data

print("Loading... { curve.liquidity.models }")

# @timed
def get_df_processed_liquidity(df_liquidity):
    output = []
    all_by_gauge_address = {}
    period_filtered_by_gauge = {}
    for index, row in df_liquidity.iterrows():
        # Rotate Through Liquidity
        date = row['date_day']
        date = dt.strptime(date[:10],'%Y-%m-%d')
        current_bal =  float(row['current_bal']) if row['current_bal'] else 0
        current_bal_usd = float(row['current_bal_usd']) if row['current_bal_usd'] else 0
        pool_address = row['pool_address']
        pool_name = row['pool_name']
        # if pool_address == '0xdc24316b9ae028f1497c275eb9192a3ea0f67022':
        #     print(f"Date: {date}")
        #     print(f"Current_bal: {current_bal}") 
        tradeable_assets = row['tradeable_assets']
        # tradeable_assets = [x.strip() for x in tradeable_assets.split(',')]
        # Get gauge info for pool 
        # if pool_address == '0xaeda92e6a3b1028edc139a4ae56ec881f3064d4f':
        #     print("\n\neusd")

        try:
            if pool_address in gauge_registry.pools:
                gauge_addr = gauge_registry.pools[pool_address].gauge_addr
            else: 
                # print("Couldn't find in gauge_registry")
                continue

            # Minimize filter by gauge address
            if not gauge_addr in all_by_gauge_address:
                df_all_by_gauge_search = df_all_by_gauge[
                    df_all_by_gauge.gauge_addr.isin([gauge_addr])
                ]
                all_by_gauge_address[gauge_addr] = df_all_by_gauge_search

            df_all_by_gauge_search = all_by_gauge_address[gauge_addr]
            # if pool_address == '0xaeda92e6a3b1028edc139a4ae56ec881f3064d4f':

            #     print(len(df_all_by_gauge_search))
            # Get this period end date votes per 

            # Minimize Filter by Date
            ## Store last date search
            if not gauge_addr in period_filtered_by_gauge:
                temp_df = df_all_by_gauge_search[df_all_by_gauge_search.period_end_date <= date]
                # if pool_address == '0xaeda92e6a3b1028edc139a4ae56ec881f3064d4f':
                #     print(f"Length temp {len(temp_df)}")
                #     print(f"Date {date}")
                #     print(f"{df_all_by_gauge_search.period_end_date.unique()}")
                    # print(f"period_end_date {date}")

                period_filtered_by_gauge[gauge_addr] = temp_df
            # else:
            #     if pool_address == '0xaeda92e6a3b1028edc139a4ae56ec881f3064d4f':
            #         print("Unique Period End Dates")
            #         print(period_filtered_by_gauge[gauge_addr].period_end_date.unique())
            #         print('\n')

            
            ## Get difference between Date and last Period End Date
            period_filtered_this_gauge = period_filtered_by_gauge[gauge_addr]

            if len(period_filtered_this_gauge) == 0:
                # if pool_address == '0xaeda92e6a3b1028edc139a4ae56ec881f3064d4f':
                #     print(f"Date {date}")
                #     print(f"No period filtered by this gauge {len(period_filtered_this_gauge) }")
                date_spread = 0
            else:
                date_spread = date - period_filtered_this_gauge.iloc[0]['period_end_date'] 
                date_spread = date_spread.days
            # print(f"Date Spread: {date_spread.days}")

            ## If more than a week, update vote information to more recent. 
            if date_spread > 7 or len(period_filtered_this_gauge) == 0:
                # print("more_than_a_week")
                temp_df = df_all_by_gauge_search[df_all_by_gauge_search.period_end_date < date]
                temp_df.sort_values(['period_end_date'], axis = 0, ascending = False)
                period_filtered_by_gauge[gauge_addr] = temp_df

            temp_df = period_filtered_by_gauge[gauge_addr] 

            ## Filter shitty vote percent
            try:
                vote_percent = temp_df.iloc[0]['vote_percent'] 
                if vote_percent < 0.0001:
                    liquidity_vs_percent = 0
                    liquidity_vs_votes = 0
                else:
                    liquidity_vs_percent = current_bal_usd / vote_percent
                    liquidity_vs_votes = current_bal_usd / temp_df.iloc[0]['total_vote_power']
            except Exception as e:
                # if pool_address == '0xaeda92e6a3b1028edc139a4ae56ec881f3064d4f':
                #     liquidity_vs_percent = 0
                #     print(f"Failed to calc vote percent for process pool {pool_name} \n\t {pool_address}")
                #     print(e)
                #     print(traceback.format_exc())
                continue            

            output.append({
                'date': date,
                'pool_address': pool_address,
                'pool_name': pool_name,
                'gauge_address': gauge_addr,
                'liquidity_native': current_bal,
                'liquidity': current_bal_usd,
                'total_votes': temp_df.iloc[0]['total_vote_power'],
                'symbol': temp_df.iloc[0]['symbol'],
                'percent': vote_percent,
                'liquidty_vs_percent': liquidity_vs_percent,
                'liquidty_vs_votes': liquidity_vs_votes,

                'tradeable_assets': tradeable_assets,
                'display_name': pool_name + f" ({pool_address[0:6]})",
                'display_symbol': temp_df.iloc[0]['symbol'] + f" ({pool_address[0:6]})"
                })
            
            # if pool_address == '0xaeda92e6a3b1028edc139a4ae56ec881f3064d4f':
            #     print(output[-1])

        except Exception as e:
            print(f"Could not process pool {pool_name} \n\t {pool_address}")
            print(e)
            print(traceback.format_exc())
            continue
        # if pool_address == '0xaeda92e6a3b1028edc139a4ae56ec881f3064d4f':
        #     print("-"*20)
    out_df = pd.json_normalize(output)
    try:
        out_df = out_df.sort_values(['date', 'liquidity'], axis = 0, ascending = False)
    except:
        pass
    return out_df

# def get_liquidity_comparison(df_processed_liquidity, filter_asset):
#     if filter_asset:
#         local_df_all = df_processed_liquidity[df_processed_liquidity['tradeable_assets'].str.contains(filter_asset)]

#         local_df = local_df_all[local_df_all['date'] == local_df_all.date.max()]

#         local_df = local_df.sort_values(['liquidity'], axis = 0, ascending = False)
#     # local_df_all = local_df_all.sort_values(["date", 'liquidity'], axis = 0, ascending = False)
#     else:
#         local_df = df_processed_liquidity[df_processed_liquidity['date'] == df_processed_liquidity.date.max()]

#         local_df = local_df.sort_values(['liquidity'], axis = 0, ascending = False)


#     return local_df



# @timed
def get_df_liquidity():
    try:
        filename = 'liquidity_general' #+ current_file_title
        resp_dict = read_csv(filename, 'source')
        df_liquidity = pd.json_normalize(resp_dict)
        df_liquidity = df_liquidity.sort_values("date_day", axis = 0, ascending = True)

    except:
        filename = 'liquidity_general' #+ fallback_file_title
        resp_dict = read_json(filename, 'source')
        df_liquidity = pd.json_normalize(resp_dict)
        df_liquidity = df_liquidity.sort_values("DATE_DAY", axis = 0, ascending = True)
    return df_liquidity


df_liquidity = get_df_liquidity()

df_processed_liquidity = get_df_processed_liquidity(df_liquidity)


try:
    app.config['df_liquidity'] = df_liquidity
    app.config['df_processed_liquidity'] = df_processed_liquidity
except:
    print("could not register in app.config\n\tLiquidity")

