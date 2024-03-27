from flask import current_app as app
from app.data.reference import filename_votium_v2
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
try:
    # df_curve_liquidity = app.config['df_curve_liquidity']
    df_curve_gauge_registry = app.config['df_curve_gauge_registry']

except:
    # from app.curve.liquidity.models import df_curve_liquidity
    from app.curve.gauges.models import df_curve_gauge_registry

print("Loading... { convex.votium_v2.models }")

# def nullify_amount(value):
#     if value == 'null' or value == '' or value == '-':
#         return np.nan
#     return float(value)

def format_df(df):
    key_list = df.keys()
    # All

    if 'checkpoint_id' in key_list:
        df['checkpoint_id']  = df['checkpoint_id'].astype(int)
    if 'checkpoint_timestamp' in key_list:
        df['checkpoint_timestamp']       = pd.to_datetime(df['checkpoint_timestamp'])
    if 'votium_round' in key_list:
        df['votium_round']  = df['votium_round'].astype(int)
    if 'gauge_addr' in key_list:
        pass
    if 'gauge_name' in key_list:
        pass
    if 'gauge_symbol' in key_list:
        pass
    if 'bounty_value' in key_list:
        df['bounty_value']= df.apply(
            lambda x: nullify_amount(x['bounty_value']), 
            axis=1)
    if 'bounty_amount' in key_list:
        df['bounty_amount']= df.apply(
            lambda x: nullify_amount(x['bounty_amount']), 
            axis=1)
    if 'total_vote_power' in key_list:
        df['total_vote_power']= df.apply(
            lambda x: nullify_amount(x['total_vote_power']), 
            axis=1)
    if 'total_vote_percent' in key_list:
        df['total_vote_percent']= df.apply(
            lambda x: nullify_amount(x['total_vote_percent']), 
            axis=1)
    if 'relative_vote_power' in key_list:
        df['relative_vote_power']= df.apply(
            lambda x: nullify_amount(x['relative_vote_power']), 
            axis=1)
    if 'bounty_per_vecrv' in key_list:
        df['bounty_per_vecrv']= df.apply(
            lambda x: nullify_amount(x['bounty_per_vecrv']), 
            axis=1)
    if 'bounty_per_vecrv_percent' in key_list:
        df['bounty_per_vecrv_percent']= df.apply(
            lambda x: nullify_amount(x['bounty_per_vecrv_percent']), 
            axis=1)
    if 'vecrv_per_bounty' in key_list:
        df['vecrv_per_bounty']= df.apply(
            lambda x: nullify_amount(x['vecrv_per_bounty']), 
            axis=1)
    if 'vecrv_percent_per_bounty' in key_list:
        df['vecrv_percent_per_bounty']= df.apply(
            lambda x: nullify_amount(x['vecrv_percent_per_bounty']), 
            axis=1)

    return df

def get_df(filename):
    df = csv_to_df(filename, 'processed')
    df = format_df(df)
    return df

df_votium_v2 = get_df(filename_votium_v2)

try:
    app.config['df_votium_v2'] = df_votium_v2

except:
    print("could not register in app.config\n\tVotium v2")

