from app.data.flipside_api_helper import fetch_and_save_data
from app.data.reference import filename_stakedao_locker


def generate_query(min_block_timestamp=None):
    stakedao_vote_locker = '0x0C30476f66034E11782938DF8e4384970B6c9e8a'

    if min_block_timestamp:
        filter_line = f"AND BLOCK_TIMESTAMP >= '{min_block_timestamp}'"
    else:
        filter_line = ""

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
    WHERE CONTRACT_ADDRESS = lower('{stakedao_vote_locker}')
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
    WHERE CONTRACT_ADDRESS = lower('{stakedao_vote_locker}')
    AND event_name = 'Withdraw'
    {filter_line}
    )


    SELECT * from deposits
    UNION ALL
    SELECT * from withdraws
    """
    return query

# def generate_query(min_block_timestamp=None):

#     if min_block_timestamp:
#         filter_line = f"AND BLOCK_TIMESTAMP >= '{min_block_timestamp}'"
#     else:
#         filter_line = ""

#     query = f"""
#     with supply as (
#     SELECT
#     BLOCK_TIMESTAMP as block_timestamp,
#     CONTRACT_NAME as contract_name,
#     EVENT_NAME as event_name,
#     (TO_NUMBER(DECODED_LOG:prevSupply::string) / POW(10,18)) as previous_supply,
#     (TO_NUMBER(DECODED_LOG:value::string) / POW(10,18)) as value,
#     ORIGIN_FROM_ADDRESS as origin_from_address,
#     TX_HASH as tx_hash
#     FROM ethereum.core.ez_decoded_event_logs
#     WHERE CONTRACT_ADDRESS = lower('0x0C30476f66034E11782938DF8e4384970B6c9e8a') -- veSDT Locker
#     AND EVENT_NAME in ('Supply')
#     {filter_line}
#     ),

#     deposit as (
#     SELECT
#     BLOCK_TIMESTAMP as block_timestamp,
#     CONTRACT_NAME as contract_name,
#     EVENT_NAME as event_name,
#     DECODED_LOG:provider::string as provider,
#     (TO_NUMBER(DECODED_LOG:value::string) / POW(10,18)) as value,
#     DECODED_LOG:ts::int as ts,
#     DECODED_LOG:locktime::int as locktime,
#     DECODED_LOG:type::int as type,
#     ORIGIN_FROM_ADDRESS as origin_from_address,
#     TX_HASH as tx_hash
#     FROM ethereum.core.ez_decoded_event_logs
#     WHERE CONTRACT_ADDRESS = lower('0x0C30476f66034E11782938DF8e4384970B6c9e8a') -- veSDT Locker
#     AND EVENT_NAME in ('Deposit')
#     {filter_line}
#     ),

#     withdraw as (

#     SELECT
#     BLOCK_TIMESTAMP as block_timestamp,
#     CONTRACT_NAME as contract_name,
#     EVENT_NAME as event_name,
#     DECODED_LOG:provider::string as provider,
#     (TO_NUMBER(DECODED_LOG:value::string) / POW(10,18)) as value,
#     DECODED_LOG:ts::int as ts,
#     ORIGIN_FROM_ADDRESS as origin_from_address,
#     TX_HASH as tx_hash
#     FROM ethereum.core.ez_decoded_event_logs
#     WHERE CONTRACT_ADDRESS = lower('0x0C30476f66034E11782938DF8e4384970B6c9e8a') -- veSDT Locker
#     AND EVENT_NAME in ('Withdraw')
#     {filter_line}
#     )


#     SELECT
#     block_timestamp,
#     contract_name,
#     event_name,
#     -- supply
#     previous_supply,
#     value,
#     -- deposit
#     NULL as provider,
#     -- value,
#     NULL as ts,
#     NULL as locktime,
#     NULL as type,
#     -- withdraw
#     -- provider,
#     -- value,
#     -- ts,
#     -- general
#     origin_from_address,
#     tx_hash
#     FROM supply
#     UNION ALL
#     SELECT
#     block_timestamp,
#     contract_name,
#     event_name,
#     -- supply
#     NULL as previous_supply,
#     -- value,
#     -- deposit
#     value,
#     provider,
#     ts,
#     locktime,
#     type,
#     -- withdraw
#     -- provider,
#     -- value,
#     -- ts,
#     -- general
#     origin_from_address,
#     tx_hash
#     FROM deposit
#     UNION ALL
#     SELECT
#     block_timestamp,
#     contract_name,
#     event_name,
#     -- supply
#     NULL as previous_supply,
#     -- value,
#     -- deposit
#     value,
#     provider,
#     ts,
#     NULL as locktime,
#     NULL as type,
#     -- withdraw
#     -- provider,
#     -- value,
#     -- ts,
#     -- general
#     origin_from_address,
#     tx_hash
#     FROM withdraw
#     ORDER BY block_timestamp DESC
#     """
#     return query


def fetch(fetch_initial = False):
    print("Fetching... { stakedao.locker.models }")

    filename = filename_stakedao_locker
    df = fetch_and_save_data(filename, generate_query, fetch_initial)
    return df




