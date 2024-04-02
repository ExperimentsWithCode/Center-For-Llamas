from flask import current_app as app
from app.data.reference import filename_curve_crv_pricing

from app.data.local_storage import (
    pd,
    read_json,
    read_csv,
    write_dataframe_csv,
    write_dfs_to_xlsx,
    csv_to_df,
    write_dataframe_csv
    )

# filename = 'crv_locker_logs'

from datetime import datetime as dt

from app.utilities.utility import get_checkpoint_id, get_checkpoint_timestamp_from_id, convert_units
from app.data.reference import (
    known_large_curve_holders,
    current_file_title,
    fallback_file_title
)

from app.data.source.chain_ids import chain_id_map


def get_aggs(df):
    df['checkpoint_id'] = df['block_timestamp'].apply(get_checkpoint_id)
    df['checkpoint_timestamp'] = df['checkpoint_id'].apply(get_checkpoint_timestamp_from_id)

    processed_agg = df[['checkpoint_id', 'checkpoint_timestamp', 'price']].groupby([
            'checkpoint_id',
            'checkpoint_timestamp'
        ]).agg(
        average_price=pd.NamedAgg(column='balance_delta', aggfunc='mean'),
    ).reset_index()
    processed_agg = self.sort(processed_agg, 'checkpoint_id')
    processed_agg['total_locked_balance'] = processed_agg['balance_delta'].transform(pd.Series.cumsum)
    self.processed_agg = processed_agg


# HOUR
# TOKEN_ADDRESS
# SYMBOL
# DECIMALS
# PRICE
# IS_IMPUTED
# EZ_HOURLY_TOKEN_PRICES_ID
# INSERTED_TIMESTAMP
# MODIFIED_TIMESTAMP


def get_df():
    filename = filename_curve_crv_pricing    # _'+ current_file_title
    df_gauge_pool_map = csv_to_df(filename, 'raw_data')
    # df_gauge_pool_map = df_gauge_pool_map.sort_values("BLOCK_TIMESTAMP", axis = 0, ascending = True)
    return df_gauge_pool_map

def process_and_save():
    print("Processing... { curve.crv_pricing.models }")

    crv_pricing = get_aggs(get_df())

    df = pd.json_normalize(crv_pricing.format_output())
    write_dataframe_csv(filename_curve_crv_pricing, df, 'processed')
    try:
        app.config['df_curve_crv_pricing'] = df
        app.config['crv_pricing'] = crv_pricing
    except:
        print("could not register in app.config\n\tGauges")
    return df

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
