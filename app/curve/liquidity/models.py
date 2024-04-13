from flask import current_app as app
from app.data.reference import (
    filename_curve_liquidity, 
    filename_curve_liquidity_aggregate,
    filename_curve_liquidity_swaps,
    filename_curve_liquidity_oracle_aggregate
)
from app.utilities.utility import nullify_amount

from app.data.local_storage import (
    pd,
    read_json,
    read_csv,
    write_dataframe_csv,
    write_dfs_to_xlsx,
    csv_to_df
    )

from app.utilities.utility import timed
from app.curve.liquidity.process_based import ProcessBasedLiquidity

from app.curve.liquidity.process_flipside import process_checkpoint_aggs

try:
    # df_curve_liquidity = app.config['df_curve_liquidity']
    df_curve_gauge_registry = app.config['df_curve_gauge_registry']

except:
    # from app.curve.liquidity.models import df_curve_liquidity
    from app.curve.gauges.models import df_curve_gauge_registry

 
    print("Loading... { curve.liquidity.models }")

# def nullify_amount(value):
#     if value == 'null' or value == '' or value == '-':
#         return np.nan
#     return float(value)

def format_df(df):
    key_list = df.keys()
    # All
    if 'balance' in key_list:
        df['balance']  = df['balance'].astype(float)

    if 'balance_usd' in key_list:
        df['balance_usd'] = df.apply(
            lambda x: nullify_amount(x['balance_usd']), 
            axis=1)

    if 'calc_price' in key_list:
        df['calc_price']= df.apply(
            lambda x: nullify_amount(x['calc_price']), 
            axis=1)

    if 'price' in key_list:
        df['price']= df.apply(
            lambda x: nullify_amount(x['price']), 
            axis=1)
        
    if 'amount' in key_list:
        df['amount']= df.apply(
            lambda x: nullify_amount(x['amount']), 
            axis=1)
        
    if 'total_balance' in key_list:
        df['total_balance']  = df['total_balance'].astype(float)

    if 'total_balance_usd' in key_list:
        df['total_balance_usd'] = df.apply(
            lambda x: nullify_amount(x['total_balance_usd']), 
            axis=1)
        
    if 'total_vote_power' in key_list:
        df['total_vote_power']= df.apply(
            lambda x: nullify_amount(x['total_vote_power']), 
            axis=1)
    if 'total_vote_percent' in key_list:
        df['total_vote_percent']= df.apply(
            lambda x: nullify_amount(x['total_vote_percent']), 
            axis=1)
        
    if 'liquidity_usd_over_votes' in key_list:
        df['liquidity_usd_over_votes']= df.apply(
            lambda x: nullify_amount(x['liquidity_usd_over_votes']), 
            axis=1)
    if 'liquidity_over_votes' in key_list:
        df['liquidity_over_votes']= df.apply(
            lambda x: nullify_amount(x['liquidity_over_votes']), 
            axis=1)
        
    if 'block_timestamp' in key_list:
        df['block_timestamp']       = pd.to_datetime(df['block_timestamp'])

    if 'checkpoint_id' in key_list:
        df['checkpoint_id']       = df['checkpoint_id'].astype(int)

    if 'checkpoint_timestamp' in key_list:
        df['checkpoint_timestamp']       = pd.to_datetime(df['checkpoint_timestamp'])

    if 'calc_price' in key_list:
        df['calc_price']         = df['calc_price'].astype(float)
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
df_curve_swaps = get_df(filename_curve_liquidity_swaps) 
df_curve_oracles_agg = get_df(filename_curve_liquidity_oracle_aggregate) 

pbl = ProcessBasedLiquidity(df_curve_gauge_registry, df_curve_liquidity)
df_curve_rebased_liquidity = pbl.df_rebased_liquidity

try:
    app.config['df_curve_liquidity'] = df_curve_liquidity
    app.config['df_curve_liquidity_aggregates'] = df_curve_liquidity_aggregates
    app.config['df_curve_rebased_liquidity'] = df_curve_rebased_liquidity
    app.config['df_curve_swaps'] = df_curve_swaps
    app.config['df_curve_oracles_agg'] = df_curve_oracles_agg

except:
    print("could not register in app.config\n\tCurve Liquidity")

