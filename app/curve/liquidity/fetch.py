from app.data.flipside_api_helper import fetch_and_save_data
from app.data.reference import filename_curve_liquidity

from app.curve.gauges.models import df_curve_gauge_registry

def generate_query(min_date=None):
    temp_list = df_curve_gauge_registry.pool_addr.unique()
    temp_list = temp_list[temp_list != '']
    pool_addresses = str(temp_list).replace('\n', ',')[1:-1]

    if min_date:
        filter_line = f"AND BLOCK_TIMESTAMP::date >= '{min_date}'"
    else:
        filter_line = ""

    query = f"""SELECT 
    bal.block_timestamp::date as date,
    bal.contract_address,
    bal.token_name,
    bal.user_address,
    bal.symbol,
    bal.has_price,
    (ifnull(bal.current_bal, 0)) as current_bal,
    (ifnull(bal.current_bal_usd, 0)) as current_bal_usd

    from ethereum.core.ez_balance_deltas as bal
    WHERE bal.USER_ADDRESS in (
    {pool_addresses}
    )
    {filter_line}
    qualify row_number() over (partition by (
    bal.block_timestamp::date,
    bal.contract_address,
    bal.token_name,
    bal.USER_ADDRESS,
    bal.symbol
    ) order by block_timestamp desc) = 1
    order by BLOCK_TIMESTAMP::date DESC
    """
    return query


def fetch(fetch_initial = False):
    filename = filename_curve_liquidity
    df = fetch_and_save_data(filename, generate_query, fetch_initial, 'date')
    return df
