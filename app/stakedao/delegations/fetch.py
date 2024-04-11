from app.data.flipside_api_helper import fetch_and_save_data
from app.data.reference import filename_stakedao_delegations
from app.utilities.utility import print_mode

def generate_query(min_block_timestamp=None):
    gnosis_delegations = '0x469788fE6E9E9681C6ebF3bF78e7Fd26Fc015446'
    space_id = '0x73646372762d676f762e65746800000000000000000000000000000000000000'

    if min_block_timestamp:
        filter_line = f"AND BLOCK_TIMESTAMP >= '{min_block_timestamp}'"
    else:
        filter_line = ""

    query = f"""
    with set_d as (
    SELECT 
    BLOCK_TIMESTAMP,
    EVENT_NAME,
    DECODED_LOG:delegate::string as delegate,
    DECODED_LOG:delegator::string as delegator,
    DECODED_LOG:id::string as id,
    ORIGIN_FROM_ADDRESS,
    TX_HASH
    FROM ethereum.core.ez_decoded_event_logs
    WHERE CONTRACT_ADDRESS = lower('{gnosis_delegations}')
    AND EVENT_NAME = 'SetDelegate'
    AND id = lower('{space_id}')
    {filter_line}
    ),

    clear_d as (
    SELECT 
    BLOCK_TIMESTAMP,
    EVENT_NAME,
    DECODED_LOG:delegate::string as delegate,
    DECODED_LOG:delegator::string as delegator,
    DECODED_LOG:id::string as id,
    ORIGIN_FROM_ADDRESS,
    TX_HASH
    FROM ethereum.core.ez_decoded_event_logs
    WHERE CONTRACT_ADDRESS = lower('{{gnosis_delegations}}')
    AND EVENT_NAME = 'ClearDelegate'
    AND id = lower('{space_id}')
    {filter_line}
    )


    SELECT 
    * 
    FROM set_d
    UNION 
    SELECT 
    * 
    FROM clear_d
    ORDER BY BLOCK_TIMESTAMP DESC
    """
    return query


def fetch(fetch_initial = False):
    print_mode("Fetching... { convex.delegates.models }")

    filename = filename_stakedao_delegations
    df = fetch_and_save_data(filename, generate_query, fetch_initial)
    return df




