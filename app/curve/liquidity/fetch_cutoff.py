from app.data.flipside_api_helper import query_and_save
from app.data.reference import filename_curve_liquidity_cutoff

from app.curve.gauges.models import df_curve_gauge_registry





def generate_query(block_timestamp_cutoff='2023-01-01 00:00:01T00:00:35.000Z'):
    temp_list = df_curve_gauge_registry.pool_addr.unique()
    temp_list = temp_list[temp_list != '']
    pool_addresses = str(temp_list).replace('\n', ',')[1:-1]

    if block_timestamp_cutoff:
        filter_line = f"AND BLOCK_TIMESTAMP < '{block_timestamp_cutoff}'"
    else:
        filter_line = ""

    chain_id = 1
    # temp_loader = True
    # if temp_loader:
    #     filter_line = f"AND BLOCK_TIMESTAMP >= '2023-08-01 00:00:01'"
    # else:
    #     filter_line = ""
        
    query = f"""

        with recieve as (
        SELECT
        sum(AMOUNT) as amount,
        SYMBOL,
        CONTRACT_ADDRESS as TOKEN_ADDR,
        TO_ADDRESS as POOL_ADDR

        FROM ethereum.core.ez_token_transfers as transfers
        WHERE transfers.TO_ADDRESS in (
        {pool_addresses}
        )
        {filter_line}
        GROUP BY ((TO_ADDRESS, CONTRACT_ADDRESS, SYMBOL))
        ),

        send as (
        SELECT
        sum(AMOUNT) as amount,
        SYMBOL,
        CONTRACT_ADDRESS as TOKEN_ADDR,
        FROM_ADDRESS as POOL_ADDR
        FROM ethereum.core.ez_token_transfers as transfers
        WHERE transfers.FROM_ADDRESS in (
        {pool_addresses}
        )
        {filter_line}
        GROUP BY ((FROM_ADDRESS, CONTRACT_ADDRESS, SYMBOL))
        ),


        recieve_native as (
        SELECT
        sum(AMOUNT) as amount,
        TO_ADDRESS as POOL_ADDR
        FROM ethereum.core.ez_native_transfers as transfers
        WHERE transfers.TO_ADDRESS in (
        {pool_addresses}
        )
        {filter_line}
        GROUP BY ((TO_ADDRESS))
        ),

        send_native as (
        SELECT
        sum(AMOUNT) as amount,
        FROM_ADDRESS as POOL_ADDR
        FROM ethereum.core.ez_native_transfers as transfers
        WHERE transfers.FROM_ADDRESS in (
        {pool_addresses}
        )
        {filter_line}
        GROUP BY ((FROM_ADDRESS))
        ),

        aggregate as (

        SELECT *
        FROM (
        -- TOKENS

        -- RECIEVE
        SELECT 
        AMOUNT,
        SYMBOL,
        TOKEN_ADDR,
        POOL_ADDR,
        {chain_id} as chain_id
        from recieve
        UNION ALL

        -- SEND
        SELECT
        -1 * AMOUNT as AMOUNT,
        SYMBOL,
        TOKEN_ADDR,
        POOL_ADDR,
        {chain_id} as chain_id
        from send
        UNION ALL
        
        -- NATIVE

        -- RECIEVE
        SELECT 
        AMOUNT,
        'ETH' as SYMBOl,
        'Native' as TOKEN_ADDR,  
        POOL_ADDR,
        {chain_id} as chain_id
        from recieve_native
        UNION ALL

        -- SEND
        SELECT
        -1* AMOUNT as AMOUNT,
        'ETH' as SYMBOl,
        'Native' as TOKEN_ADDR,  
        POOL_ADDR,
        {chain_id} as chain_id
        from send_native
        )
        )


        SELECT 
        sum(AMOUNT) as amount,
        SYMBOL,
        TOKEN_ADDR,
        POOL_ADDR,
        chain_id,
        '{block_timestamp_cutoff}' as cutoff
        from aggregate
        group by (SYMBOL, TOKEN_ADDR, POOL_ADDR, chain_id)
    """
    return query



def fetch_cutoff(cutoff_date ='2023-01-01 00:00:01'):
    # Always a single date so no need for prior data joining
    filename = filename_curve_liquidity_cutoff
    query = generate_query(cutoff_date)
    df = query_and_save(query, filename) 
    return df
