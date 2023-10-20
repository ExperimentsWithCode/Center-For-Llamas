from flask import current_app as app
from app.data.reference import filename_curve_liquidity, filename_curve_liquidity_aggregate

from app.data.local_storage import (
    pd,
    read_json,
    read_csv,
    write_dataframe_csv,
    write_dfs_to_xlsx,
    csv_to_df
    )

from app.utilities.utility import timed


print("Loading... { curve.liquidity.models }")


def format_df(df):
    key_list = df.keys()
    # All
    if 'liquidity_native' in key_list:
        df['liquidity_native']  = df['liquidity_native'].astype(float)

    if 'liquidity' in key_list:
        df['liquidity']         = df['liquidity'].astype(float)

    if 'total_votes' in key_list:
        df['total_votes']       = df['total_votes'].astype(float)

    if 'percent' in key_list:
        df['percent']           = df['percent'].astype(float)

    if 'date' in key_list:
        df['date']       = pd.to_datetime(df['date']).dt.date

    # if 'liquidity_over_votes' in key_list:
    #     df['liquidity_over_votes'] = df['liquidity_over_votes'].astype(float)

    # if 'liquidity_native_over_votes' in key_list:
    #     df['liquidity_over_votes'] = df['liquidity_over_votes'].astype(float)

    return df

def get_df(filename):
    df = csv_to_df(filename, 'processed')
    df = format_df(df)
    return df

df_curve_liquidity = get_df(filename_curve_liquidity)
df_curve_liquidity_aggregates = get_df(filename_curve_liquidity_aggregate) 

try:
    app.config['df_curve_liquidity'] = df_curve_liquidity
    app.config['df_curve_liquidity_aggregates'] = df_curve_liquidity_aggregates
except:
    print("could not register in app.config\n\tCurve Liquidity")

