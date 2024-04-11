from app.data.flipside_api_helper import fetch_and_save_data
from app.data.reference import filename_curve_gauges
from app.utilities.utility import print_mode

def generate_query(min_block_timestamp=None):
    curve_voter_address = '0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB'

    if min_block_timestamp:
        filter_line = f"AND BLOCK_TIMESTAMP >= '{min_block_timestamp}'"
    else:
        filter_line = ""

    query = f"""
    -- 0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB
    with gauge_types as (
    SELECT 
        DECODED_LOG:name::string as name,
        DECODED_LOG:type_id::int as type_id,
        BLOCK_TIMESTAMP as block_timestamp,
        TX_HASH as tx_hash
    
    FROM ethereum.core.ez_decoded_event_logs LOGS
    LEFT JOIN ethereum.core.dim_contracts CONTRACT
        ON CONTRACT.address = lower(LOGS.DECODED_LOG:gauge_addr::string)
    WHERE CONTRACT_ADDRESS = lower('{curve_voter_address}')
    AND EVENT_NAME = 'AddType'
    ),

    new_type_weight as (
    SELECT 
        ifnull(DECODED_LOG:time::int, 0) as time,
        DECODED_LOG:total_weight::string as total_weight,
        ifnull(DECODED_LOG:type_id::int, 0) as type_id,
        DECODED_LOG:weight::string as weight,
        TX_HASH,
        BLOCK_TIMESTAMP
    
    FROM ethereum.core.ez_decoded_event_logs
    WHERE CONTRACT_ADDRESS = lower('{curve_voter_address}')
    AND EVENT_NAME = 'NewTypeWeight'
    ORDER BY BLOCK_TIMESTAMP ASC

    ),

    new_gauges as (

    SELECT 
        SYMBOL, 
        NAME, 
        DECODED_LOG:addr::string as gauge_addr,
        DECODED_LOG:gauge_type::int as gauge_type,
        DECODED_LOG:weight::int as weight,
        TX_HASH,
        BLOCK_TIMESTAMP
    
    FROM ethereum.core.ez_decoded_event_logs LOGS
    LEFT JOIN ethereum.core.dim_contracts CONTRACT
        ON CONTRACT.address = lower(LOGS.DECODED_LOG:addr::string)
    WHERE CONTRACT_ADDRESS = lower('{curve_voter_address}')
    AND EVENT_NAME = 'NewGauge'
    ORDER BY BLOCK_TIMESTAMP ASC
    
    ),

    gauge_meta as (
    SELECT 
        new_gauges.gauge_type as type_id,
        gauge_types.name as type_name,
        new_gauges.name,
        new_gauges.symbol,
        new_gauges.gauge_addr,
        new_gauges.weight,
        new_type_weight.weight as type_weight,
        new_type_weight.total_weight as type_total_weight,
        new_type_weight.time as type_weight_time,
        new_gauges.tx_hash,
        new_gauges.block_timestamp as vote_timestamp
    FROM new_gauges 
    LEFT JOIN gauge_types
    ON new_gauges.gauge_type = gauge_types.type_id
    LEFT JOIN new_type_weight
    ON new_gauges.gauge_type = new_type_weight.type_id
    ORDER BY new_gauges.block_timestamp DESC
    ),


    -- BREAK between meta and deployers

    v2_deployer as (
    SELECT
        BLOCK_TIMESTAMP as block_timestamp,
        DECODED_LOG:gauge::string as gauge_addr,
        DECODED_LOG:pool::string as pool_addr,
        DECODED_LOG:token::string as token_addr,
        'v2' as source
    
    
    FROM ethereum.core.ez_decoded_event_logs
    WHERE CONTRACT_ADDRESS = lower('0xF18056Bbd320E96A48e3Fbf8bC061322531aac99') -- v2 deployer
    AND EVENT_NAME = 'LiquidityGaugeDeployed'
    {filter_line}

    ),

    factory_deployer as (
    SELECT 
        BLOCK_TIMESTAMP as block_timestamp,
        DECODED_LOG:gauge::string as gauge_addr,
        DECODED_LOG:pool::string as pool_addr,
        '' as token_addr,
        'factory' as source

    FROM ethereum.core.ez_decoded_event_logs as logs

    WHERE logs.CONTRACT_ADDRESS = lower('0xB9fC157394Af804a3578134A6585C0dc9cc990d4')  -- factory
    AND logs.EVENT_NAME = 'LiquidityGaugeDeployed'
    {filter_line}

    ),


    stable_deployer as (
    SELECT 
        BLOCK_TIMESTAMP as block_timestamp,
        DECODED_LOG:gauge::string as gauge_addr,
        DECODED_LOG:pool::string as pool_addr,
        '' as token_addr,
        'stable_factory' as source

    FROM ethereum.core.ez_decoded_event_logs as logs

    WHERE logs.CONTRACT_ADDRESS = lower('0x4F8846Ae9380B90d2E71D5e3D042dff3E7ebb40d')  -- factory
    AND logs.EVENT_NAME = 'LiquidityGaugeDeployed'
    {filter_line}

    ),


    multichain_deployer as (
    SELECT 
        BLOCK_TIMESTAMP as block_timestamp,
        DECODED_LOG:_gauge::string as gauge_addr,
        DECODED_LOG:_chain_id::string as chain_id,
        DECODED_LOG:_deployer::string as deployer,
        DECODED_LOG:_implementation::string as implementation,
        DECODED_LOG:_salt::string as salt,
        '' as pool_addr,
        '' as token_addr,
        'multichain_factory' as source

    FROM ethereum.core.ez_decoded_event_logs as logs

    WHERE logs.CONTRACT_ADDRESS = lower('0xabc000d88f23bb45525e447528dbf656a9d55bf5')  -- factory
    AND logs.EVENT_NAME = 'DeployedGauge'
    {filter_line}

    ),


    tricrypto_deployer as (
    SELECT 
        BLOCK_TIMESTAMP as block_timestamp,
        DECODED_LOG:gauge::string as gauge_addr,
        DECODED_LOG:pool::string as pool_addr,
        '' as token_addr,
        'tricrypto_factory' as source

    FROM ethereum.core.ez_decoded_event_logs as logs

    WHERE logs.CONTRACT_ADDRESS = lower('0x0c0e5f2ff0ff18a3be9b835635039256dc4b4963')  -- tricrypto_factory
    AND logs.EVENT_NAME = 'LiquidityGaugeDeployed'
    {filter_line}

    ),

    
    stableswap_ng as (
    SELECT 
        BLOCK_TIMESTAMP as block_timestamp,
        DECODED_LOG:gauge::string as gauge_addr,
        DECODED_LOG:pool::string as pool_addr,
        '' as token_addr,
        'stableswap_ng' as source
    FROM ethereum.core.ez_decoded_event_logs as logs

    WHERE logs.CONTRACT_ADDRESS = lower('0x6A8cbed756804B16E05E741eDaBd5cB544AE21bf')  -- factory
    AND logs.EVENT_NAME = 'LiquidityGaugeDeployed'
    ),

    combo as (
    SELECT gauge_addr, pool_addr, token_addr, source, block_timestamp, '' as chain_id FROM v2_deployer
    UNION
    SELECT gauge_addr, pool_addr, token_addr, source, block_timestamp,'' as chain_id   FROM factory_deployer
    UNION
    SELECT gauge_addr, pool_addr, token_addr, source, block_timestamp,'' as chain_id FROM stable_deployer
    UNION
    SELECT gauge_addr, pool_addr, token_addr, source, block_timestamp,'' as chain_id FROM tricrypto_deployer
    UNION
    SELECT gauge_addr, pool_addr, token_addr, source, block_timestamp, chain_id  FROM multichain_deployer
    UNION
    SELECT gauge_addr, pool_addr, token_addr, source, block_timestamp, '' as chain_id  FROM stableswap_ng

    ),


    deployer_meta as (
    SELECT 
        combo.gauge_addr as gauge_addr, 
        combo.pool_addr as pool_addr, 
        combo.token_addr as token_addr, 
        combo.source as source, 
        combo.chain_id as chain_id,
        combo.block_timestamp as block_timestamp,
        contracts.NAME as gauge_name,
        contracts.SYMBOL as gauge_symbol,
        pool_contracts.NAME as pool_name,
        pool_contracts.SYMBOL as pool_symbol,
        token_contracts.NAME as token_name,
        token_contracts.SYMBOL as token_symbol
    FROM combo
    LEFT JOIN ethereum.core.dim_contracts as contracts
        ON combo.gauge_addr = contracts.ADDRESS
    LEFT JOIN ethereum.core.dim_contracts as pool_contracts
        ON combo.pool_addr = pool_contracts.ADDRESS
    LEFT JOIN ethereum.core.dim_contracts as token_contracts
        ON combo.token_addr = token_contracts.ADDRESS
    )


    SELECT 
        gauge_meta.type_id,
        gauge_meta.type_name,
        IFNULL(gauge_meta.name, deployer_meta.gauge_name) as name,
        IFNULL(gauge_meta.symbol, deployer_meta.gauge_symbol) as symbol,
        IFNULL(gauge_meta.gauge_addr, deployer_meta.gauge_addr) as gauge_addr,
        gauge_meta.weight,
        gauge_meta.type_weight,
        gauge_meta.type_total_weight,
        gauge_meta.type_weight_time,
        gauge_meta.tx_hash,
        gauge_meta.vote_timestamp,

        deployer_meta.pool_addr, 
        deployer_meta.token_addr, 
        deployer_meta.source, 
        deployer_meta.block_timestamp as deployed_timestamp,
        deployer_meta.gauge_name,
        deployer_meta.gauge_symbol,
        deployer_meta.pool_name,
        deployer_meta.pool_symbol,
        deployer_meta.token_name,
        deployer_meta.token_symbol,
        deployer_meta.chain_id
    FROM gauge_meta
    FULL JOIN deployer_meta
    ON gauge_meta.gauge_addr = deployer_meta.gauge_addr
    ORDER BY deployed_timestamp DESC
    """
    return query


def fetch(fetch_initial = False):
    print_mode("Fetching... { curve.gauges.models }")

    filename = filename_curve_gauges
    df = fetch_and_save_data(filename, generate_query, fetch_initial, 'deployed_timestamp')
    return df




