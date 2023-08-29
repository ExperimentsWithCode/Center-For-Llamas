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

import ast
from datetime import datetime as dt

try:
    df_all_by_gauge = app.config['df_all_by_gauge']
    gauge_registry = app.config['gauge_registry']

except:
    from app.curve.gauge_rounds.models import df_all_by_gauge
    from app.curve.gauges.models import gauge_registry

    # from app.curve.locker.models import df_history_data


def get_df_processed_liquidity(df_liquidity):
    output = []
    for index, row in df_liquidity.iterrows():
        date = row['DATE_DAY']
        current_bal = row['CURRENT_BAL']
        current_bal_usd = row['CURRENT_BAL_USD']

        pool_address = row['POOL_ADDRESS']
        pool_name = row['POOL_NAME']
        tradeable_assets = row['TRADEABLE_ASSETS']
        # tradeable_assets = [x.strip() for x in tradeable_assets.split(',')]

        try:
            gauge_addr = gauge_registry.pools[pool_address].gauge_addr

            df_all_by_gauge_search = df_all_by_gauge[
                df_all_by_gauge.gauge_addr.isin([gauge_addr])
            ]

            temp_df = df_all_by_gauge_search[df_all_by_gauge_search.period_end_date < date]
            temp_df.sort_values(['period_end_date'], axis = 0, ascending = False)
            try:
                vote_percent = temp_df.iloc[0]['vote_percent'] 
                if vote_percent < 0.001:
                    # print(f"Not enough vote percent to process pool {pool_name} \n\t {pool_address}")
                    continue
            except Exception as e:
                # print(f"Failed to calc vote percent for process pool {pool_name} \n\t {pool_address}")
                # print(e)
                # print(traceback.format_exc())
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
                'percent': temp_df.iloc[0]['vote_percent'],
                'liquidty_vs_percent': current_bal_usd / temp_df.iloc[0]['vote_percent'] ,
                'tradeable_assets': tradeable_assets,
                'display_name': pool_name + f" ({pool_address[0:6]})",
                'display_symbol': temp_df.iloc[0]['symbol'] + f" ({pool_address[0:6]})"


                })
        except Exception as e:
            # print(f"Could not process pool {pool_name} \n\t {pool_address}")
            # print(e)
            # print(traceback.format_exc())
            continue

    return pd.json_normalize(output)




def get_df_liquidity():
    # try:
    #     filename = 'liquidity_general' #+ current_file_title
    #     resp_dict = read_csv(filename, 'source')
    #     df_liquidity = pd.json_normalize(resp_dict)
    #     df_liquidity = df_liquidity.sort_values("BLOCK_TIMESTAMP", axis = 0, ascending = True)

    # except:
    filename = 'liquidity_general3' #+ fallback_file_title
    resp_dict = read_json(filename, 'source')
    df_liquidity = pd.json_normalize(resp_dict)
    df_liquidity = df_liquidity.sort_values("DATE_DAY", axis = 0, ascending = False)

    return df_liquidity


df_liquidity = get_df_liquidity()

df_processed_liquidity = get_df_processed_liquidity(df_liquidity)


try:
    app.config['df_liquidity'] = df_liquidity
    app.config['df_processed_liquidity'] = df_processed_liquidity
except:
    print("could not register in app.config\n\tLiquidity")