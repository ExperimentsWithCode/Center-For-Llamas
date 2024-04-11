from app.data.flipside_api_helper import fetch_and_save_data
from app.data.reference import filename_stakedao_staked_sdcrv 

def generate_query(min_block_timestamp=None):
    cxv_locker = '0x72a19342e8F1838460eBFCCEf09F6585e32db86E'

    if min_block_timestamp:
        filter_line = f"AND BLOCK_TIMESTAMP >= '{min_block_timestamp}'"
    else:
        filter_line = ""

    query = f"""
    with deposit_withdraw as (
    SELECT
        BLOCK_TIMESTAMP as block_timestamp,
        CONTRACT_NAME as contract_name,
        CONTRACT_ADDRESS as contract_address,
        EVENT_NAME as event_name,
        DECODED_LOG:provider::string as provider,
        (TO_NUMBER(DECODED_LOG:value::string) / POW(10,18)) as value,
        ORIGIN_FROM_ADDRESS as origin_from_address,
        TX_HASH as tx_hash
        FROM ethereum.core.ez_decoded_event_logs
        WHERE CONTRACT_ADDRESS = lower('0x7f50786A0b15723D741727882ee99a0BF34e3466') -- sdCRV Gauge
        AND EVENT_NAME in ('Withdraw', 'Deposit')
        {filter_line}   

    ),

    transfers as (
    SELECT
        BLOCK_TIMESTAMP as block_timestamp,
        CONTRACT_NAME as contract_name,
        CONTRACT_ADDRESS as contract_address,
        EVENT_NAME as event_name,
        DECODED_LOG:_to::string as provider,
        DECODED_LOG:_from::string as old_provider,
        (TO_NUMBER(DECODED_LOG:_value::string) / POW(10,18)) as value,
        ORIGIN_FROM_ADDRESS as origin_from_address,
        TX_HASH as tx_hash
        FROM ethereum.core.ez_decoded_event_logs
        WHERE CONTRACT_ADDRESS = lower('0x7f50786A0b15723D741727882ee99a0BF34e3466') -- sdCRV Gauge
        AND EVENT_NAME in ('Transfer')
        AND not DECODED_LOG:_to::string = '0x0000000000000000000000000000000000000000'
        and not DECODED_LOG:_from::string ='0x0000000000000000000000000000000000000000'
        {filter_line}

    )

    SELECT 
        block_timestamp,
        contract_name,
        contract_address,
        event_name,
        provider,
        '' as previous_provider,
        value,
        origin_from_address,
        tx_hash
    FROM deposit_withdraw
    UNION ALL 
    SELECT
        block_timestamp,
        contract_name,
        contract_address,
        event_name,
        provider,
        old_provider as previous_provider,
        value,
        origin_from_address,
        tx_hash
    FROM transfers
    UNION ALL 
    SELECT
        block_timestamp,
        contract_name,
        contract_address,
        event_name,
        old_provider as provider,
        provider as previous_provider ,
        -1 * value as value,
        origin_from_address,
        tx_hash
    FROM transfers
    

    """
    return query

def fetch(fetch_initial = False):
    print("Fetching... { convex.sdcrv_staker.models }")

    filename = filename_stakedao_staked_sdcrv
    df = fetch_and_save_data(filename, generate_query, fetch_initial)
    return df

