from app.data.flipside_api_helper import fetch_and_save_data
from app.data.reference import filename_stakedao_staked_sdcrv 

def generate_query(min_block_timestamp=None):
    cxv_locker = '0x72a19342e8F1838460eBFCCEf09F6585e32db86E'

    if min_block_timestamp:
        filter_line = f"AND BLOCK_TIMESTAMP >= '{min_block_timestamp}'"
    else:
        filter_line = ""

    query = f"""

    SELECT
    BLOCK_TIMESTAMP as block_timestamp,
    CONTRACT_NAME as contract_name,
    EVENT_NAME as event_name,
    DECODED_LOG:provider::string as provider,
    DECODED_LOG:value::string as value,
    TX_HASH as tx_hash
    FROM ethereum.core.ez_decoded_event_logs
    WHERE CONTRACT_ADDRESS = lower('0x7f50786A0b15723D741727882ee99a0BF34e3466') -- sdCRV Gauge
    AND EVENT_NAME in ('Withdraw', 'Deposit')
    {filter_line}

    """
    return query

def fetch(fetch_initial = False):
    print("Fetching... { convex.locker.models }")

    filename = filename_stakedao_staked_sdcrv
    df = fetch_and_save_data(filename, generate_query, fetch_initial)
    return df

