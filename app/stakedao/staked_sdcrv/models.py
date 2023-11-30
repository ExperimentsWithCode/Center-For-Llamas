from flask import current_app as app
from app.data.reference import filename_stakedao_staked_sdcrv

from app.data.local_storage import (
    pd,
    read_json,
    read_csv,
    write_dataframe_csv,
    write_dfs_to_xlsx,
    csv_to_df
    )


from app.utilities.utility import (
    get_period_direct, 
    get_period_end_date, 
    get_date_obj, 
    get_dt_from_timestamp,
    shift_time_days,
    df_remove_nan
)


print("Loading... { stakedao.staked_sdcrv.models }")


def format_df(df):
    key_list = df.keys()
    if 'block_timestamp' in key_list:
        df['block_timestamp'] = df['block_timestamp'].apply(get_date_obj)

    if 'value' in key_list:
        df['value'] = df['value'].astype(float)

    if 'staked_balance' in key_list:
        df['staked_balance'] = df['staked_balance'].astype(float)
    
    elif 'total_staked_balance' in key_list:
        df['total_staked_balance'] = df['total_staked_balance'].astype(float)

    if 'balance_delta' in key_list:
        df['balance_delta'] = df['balance_delta'].astype(float)

    if 'date' in key_list:
        # df['epoch_end'] = df['epoch_end'].apply(get_dt_from_timestamp)
        df['date'] = pd.to_datetime(df["date"], format="%Y-%m-%d")


    return df

def get_df(filename, location):
    df = csv_to_df(filename, location)
    df = format_df(df)
    return df

df_stakedao_sdcrv = get_df(filename_stakedao_staked_sdcrv, 'processed')
df_stakedao_sdcrv_known = get_df(filename_stakedao_staked_sdcrv+"_known", 'processed')
df_stakedao_sdcrv_agg = get_df(filename_stakedao_staked_sdcrv+"_agg", 'processed')

try:
    app.config['df_stakedao_sdcrv'] = df_stakedao_sdcrv
    app.config['df_stakedao_sdcrv_known'] = df_stakedao_sdcrv_known
    app.config['df_stakedao_sdcrv_agg'] = df_stakedao_sdcrv_agg
except:
    print("could not register in app.config\n\tStakeDAO Staked sdCRV")



