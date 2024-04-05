from app.data.flipside_api_helper import fetch_and_save_data
from app.data.reference import filename_curve_locker
from app.utilities.utility import shift_time_days

def generate_query(min_block_timestamp=None):
    curve_locker_address = '0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2'

    if min_block_timestamp:
        filter_line = f"AND BLOCK_TIMESTAMP >= '{min_block_timestamp}'"
    else:
        filter_line = ""
        filter_secondary_line = ""

    query = f""" 
    with deposits as (
    SELECT 
    BLOCK_TIMESTAMP as block_timestamp,
    CONTRACT_ADDRESS as contract_address,
    CONTRACT_NAME as contract_name,
    EVENT_NAME as event_name,
    (TO_NUMBER(DECODED_LOG:value::string) / POW(10,18)) as value,
    DECODED_LOG:ts::int as ts,
    DECODED_LOG:provider::string as provider,
    DECODED_LOG:locktime::int as locktime,
    DECODED_LOG:type::int as type,
    ORIGIN_FROM_ADDRESS as origin_from_address,
    tx_hash as tx_hash
    FROM ethereum.core.ez_decoded_event_logs
    WHERE CONTRACT_ADDRESS = lower('{curve_locker_address}')
    AND event_name = 'Deposit'
    {filter_line}
    ),
    
    withdraws as (
    SELECT 
    BLOCK_TIMESTAMP as block_timestamp,
    CONTRACT_ADDRESS as contract_address,
    CONTRACT_NAME as contract_name,
    EVENT_NAME as event_name,
    (TO_NUMBER(DECODED_LOG:value::string) / POW(10,18)) as value,
    DECODED_LOG:ts::int as ts,
    DECODED_LOG:provider::string as provider,
    DECODED_LOG:ts::int as locktime,
    -1 as type,
    ORIGIN_FROM_ADDRESS as origin_from_address,
    tx_hash as tx_hash
    FROM ethereum.core.ez_decoded_event_logs
    WHERE CONTRACT_ADDRESS = lower('{curve_locker_address}')
    AND event_name = 'Withdraw'
    {filter_line}
    )


    SELECT * from deposits
    UNION ALL
    SELECT * from withdraws
    """
    return query


def fetch(fetch_initial = False):
    filename = filename_curve_locker
    df = fetch_and_save_data(filename, generate_query, fetch_initial)
    return df
