from flask import current_app as app
from app.data.reference import filename_curve_gauges

from app.data.local_storage import (
    pd,
    read_json,
    read_csv,
    write_dataframe_csv,
    write_dfs_to_xlsx,
    csv_to_df
    )
from app.curve.gauges.process_flipside import process_and_get, process_and_save

from app.utilities.utility import nullify_amount

try:
    from config import activate_print_mode
except:
    activate_print_mode = False

if activate_print_mode:
    print("Loading... { curve.gauges.models }")


def format_df(df):
    # df['gauge_addr']            = df['gauge_addr'].astype(str)
    # df['gauge_name']            = df['gauge_name'].astype(str)
    # df['gauge_symbol']          = df['gauge_symbol'].astype(str)
    # df['pool_addr']             = df['pool_addr'].astype(str)
    # df['pool_name']             = df['pool_name'].astype(str)
    # df['pool_symbol']           = df['pool_symbol'].astype(str)
    # df['pool_partial']          = df['pool_partial'].astype(str)
    # df['token_addr']            = df['token_addr'].astype(str)
    # df['token_name']            = df['token_name'].astype(str)
    # df['token_symbol']          = df['token_symbol'].astype(str)
    # df['source']                = df['source'].astype(str)
    df['deployed_timestamp']    = pd.to_datetime(df['deployed_timestamp'])
    # if 'first_period' in df.keys():
    #     df['first_period']          = df['first_period'].astype(int)
    #     df['deployed_period']          = df['deployed_period'].astype(int)

    df['first_period_end_date'] = pd.to_datetime(df['first_period_end_date']).dt.date
    df['deployed_period_end_date'] = pd.to_datetime(df['deployed_period_end_date']).dt.date

    if 'type_id' in df.keys():
        df['type_id'] = df.apply(
            lambda x: nullify_amount(x['type_id']), 
            axis=1)
        
    # df['type_name']             = df['type_name'].astype(str)
    # df['name']                  = df['name'].astype(str)
    # df['symbol']                = df['symbol'].astype(str)
    if 'weight' in df.keys():
        df['weight'] = df.apply(
            lambda x: nullify_amount(x['weight']), 
            axis=1)
    # df['type_weight']           = df['type_weight'].astype(float)
    # df['type_total_weight']     = df['type_total_weight'].astype(int)
    # df['type_weight_time']      = df['type_weight_time'].astype(int)
    # df['tx_hash']               = df['tx_hash'].astype(str)
    df['vote_timestamp'] = pd.to_datetime(df['vote_timestamp'])
    # df['chain_id']              = df['chain_id'].astype(int)
    # df['chain_name']            = df['chain_name'].astype(str)
    return df


def get_gauge_registry(is_already_borked=False):
    try:
        filename = filename_curve_gauges    # _'+ current_file_title
        df = csv_to_df(filename, 'processed')
        df = format_df(df)
    except:
        try:
            filename = filename_curve_gauges    # '+ fallback_file_title
            gauge_pool_map = read_json(filename, 'processed')
            df = pd.json_normalize(gauge_pool_map)
            df = format_df(df)
        except:
            return process_and_save()


    # df_gauge_pool_map = df_gauge_pool_map.sort_values("BLOCK_TIMESTAMP", axis = 0, ascending = True)
    return df

gauge_registry = process_and_get()
df_curve_gauge_registry = get_gauge_registry()

try:
    app.config['df_curve_gauge_registry'] = df_curve_gauge_registry
    app.config['gauge_registry'] = gauge_registry
except:
    print("could not register in app.config\n\tGauges")


# ,type_id,
# type_name,
# name,
# symbol,
# gauge_addr,
# weight,
# type_weight,
# type_total_weight,
# type_weight_time,
# tx_hash,
# vote_timestamp,
# pool_addr,
# token_addr,
# source,
# deployed_timestamp,
# gauge_name,
# gauge_symbol,
# pool_name
# ,pool_symbol
# ,token_name
# ,token_symbol
# ,__row_index
