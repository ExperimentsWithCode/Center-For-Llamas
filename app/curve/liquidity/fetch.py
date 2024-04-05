from app.data.flipside_api_helper import fetch_and_save_data
from app.data.reference import filename_curve_liquidity

from app.curve.gauges.models import df_curve_gauge_registry


from app.utilities.utility import shift_time_days


def generate_query(min_block_timestamp=None, max_block_timestamp = None):
    temp_list = df_curve_gauge_registry.pool_addr.unique()
    temp_list = temp_list[temp_list != '']
    pool_addresses = str(temp_list).replace('\n', ',')[1:-1]
    filter_secondary_line = f"AND BLOCK_TIMESTAMP <= '{shift_time_days(min_block_timestamp, 7*6) }'"

    if min_block_timestamp:
        if not max_block_timestamp:
            max_block_timestamp = shift_time_days(min_block_timestamp, 31) 
        filter_line = f"AND BLOCK_TIMESTAMP > '{min_block_timestamp}' AND BLOCK_TIMESTAMP < '{max_block_timestamp}'"
    else:
        filter_line = ""

    # temp_loader = True
    # if temp_loader:
    #     filter_line = f"AND BLOCK_TIMESTAMP >= '2023-08-01 00:00:01'"
    # else:
    #     filter_line = ""
        
    query = f"""
    with recieve as (
    SELECT
    *
    FROM ethereum.core.ez_token_transfers as transfers
    WHERE transfers.TO_ADDRESS in (
    {pool_addresses}
    )
    {filter_line}
    ),

    send as (
    SELECT
    *
    FROM ethereum.core.ez_token_transfers as transfers
    WHERE transfers.FROM_ADDRESS in (
    {pool_addresses}
    )
    {filter_line}
    ),


    recieve_native as (
    SELECT
    *
    FROM ethereum.core.ez_native_transfers as transfers
    WHERE transfers.TO_ADDRESS in (
    {pool_addresses}
    )
    {filter_line}
    ),

    send_native as (
    SELECT
    *
    FROM ethereum.core.ez_native_transfers as transfers
    WHERE transfers.FROM_ADDRESS in (
    {pool_addresses}
    )
    {filter_line}
    )

    SELECT *
    FROM (
    -- TOKENS

    -- RECIEVE
    SELECT 
    AMOUNT, 
    AMOUNT_USD,
    
    TO_ADDRESS as POOL_ADDR,
    
    SYMBOL as SYMBOl,
    TOKEN_PRICE as PRICE,
    HAS_PRICE as HAS_PRICE,

    ORIGIN_TO_ADDRESS as ORIGIN_TO_ADDRESS,
    ORIGIN_FROM_ADDRESS as ORIGIN_FROM_ADDRESS,
    FROM_ADDRESS as FROM_ADDRESS,
    TO_ADDRESS as TO_ADDRESS,
    

    CONTRACT_ADDRESS as TOKEN_ADDR,
    BLOCK_TIMESTAMP,
    TX_HASH,
    1 as chain_id
    
    from recieve
    UNION ALL

    -- SEND
    SELECT
    -1 * AMOUNT as AMOUNT, 
    -1 * AMOUNT_USD as AMOUNT_USD,
    
    FROM_ADDRESS as POOL_ADDR,
    
    SYMBOL as SYMBOl,
    TOKEN_PRICE as PRICE,
    HAS_PRICE as HAS_PRICE,
    
    ORIGIN_TO_ADDRESS as ORIGIN_TO_ADDRESS,
    ORIGIN_FROM_ADDRESS as ORIGIN_FROM_ADDRESS,
    FROM_ADDRESS as FROM_ADDRESS,
    TO_ADDRESS as TO_ADDRESS,
    
    CONTRACT_ADDRESS as TOKEN_ADDR,  
    BLOCK_TIMESTAMP,
    TX_HASH,
    1 as chain_id
    from send
    UNION ALL
    
    -- NATIVE

    -- RECIEVE
    SELECT 
    AMOUNT, 
    AMOUNT_USD,
    
    TO_ADDRESS as POOL_ADDR,
    
    'ETH' as SYMBOl,
    AMOUNT_USD / AMOUNT as PRICE,
    TRUE as HAS_PRICE,
    
    ORIGIN_TO_ADDRESS as ORIGIN_TO_ADDRESS,
    ORIGIN_FROM_ADDRESS as ORIGIN_FROM_ADDRESS,
    FROM_ADDRESS as FROM_ADDRESS,
    TO_ADDRESS as TO_ADDRESS,
    'Native' as TOKEN_ADDR,  
    BLOCK_TIMESTAMP,
    TX_HASH,
    1 as chain_id
    
    from recieve_native
    UNION ALL

    -- SEND
    SELECT
    -1 * AMOUNT as AMOUNT, 
    -1 * AMOUNT_USD as AMOUNT_USD,
    
    FROM_ADDRESS as POOL_ADDR,
    
    'ETH' as SYMBOl,
    AMOUNT_USD / AMOUNT as PRICE,
    TRUE as HAS_PRICE,
    
    ORIGIN_TO_ADDRESS as ORIGIN_TO_ADDRESS,
    ORIGIN_FROM_ADDRESS as ORIGIN_FROM_ADDRESS,
    FROM_ADDRESS as FROM_ADDRESS,
    TO_ADDRESS as TO_ADDRESS,
    'Native' as TOKEN_ADDR,  
    BLOCK_TIMESTAMP,
    TX_HASH,
    1 as chain_id
    from send_native
    )
    ORDER BY BLOCK_TIMESTAMP ASC
    """    
    return query



# def generate_query(min_date=None):
#     temp_list = df_curve_gauge_registry.pool_addr.unique()
#     temp_list = temp_list[temp_list != '']
#     pool_addresses = str(temp_list).replace('\n', ',')[1:-1]

#     if min_date:
#         filter_line = f"AND BLOCK_TIMESTAMP::date >= '{min_date}'"
#     else:
#         filter_line = ""

#     query = f"""SELECT 
#     bal.block_timestamp::date as date,
#     bal.contract_address,
#     bal.token_name,
#     bal.user_address,
#     bal.symbol,
#     bal.has_price,
#     (ifnull(bal.current_bal, 0)) as current_bal,
#     (ifnull(bal.current_bal_usd, 0)) as current_bal_usd

#     from ethereum.core.ez_balance_deltas as bal
#     WHERE bal.USER_ADDRESS in (
#     {pool_addresses}
#     )
#     {filter_line}
#     qualify row_number() over (partition by (
#     bal.block_timestamp::date,
#     bal.contract_address,
#     bal.token_name,
#     bal.USER_ADDRESS,
#     bal.symbol
#     ) order by block_timestamp desc) = 1
#     order by BLOCK_TIMESTAMP::date DESC
#     """
#     return query


def fetch(fetch_initial = False):
    filename = filename_curve_liquidity
    df = fetch_and_save_data(filename, generate_query, fetch_initial, 'block_timestamp')
    return df
