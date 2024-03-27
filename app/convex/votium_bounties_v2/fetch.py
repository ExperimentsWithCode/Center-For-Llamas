from app.data.flipside_api_helper import fetch_and_save_data
from app.data.reference import filename_votium_v2 


def generate_query(min_block_timestamp=None):
    votium_v2 = '0x63942E31E98f1833A234077f47880A66136a2D1e'

    if min_block_timestamp:
        filter_line = f"AND BLOCK_TIMESTAMP >= '{min_block_timestamp}'"
    else:
        filter_line = ""

    query = f"""
    SELECT 
    BLOCK_TIMESTAMP,
    (TO_NUMBER(DECODED_LOG:_amount::string) / POW(10,18)) as bounty_amount,
    price * bounty_amount as bounty_value,
    price as price,
    DECODED_LOG:_depositor::string as depositor,
    DECODED_LOG:_excluded as excluded,
    DECODED_LOG:_gauge::string as gauge_addr,
    DECODED_LOG:_index::int as index,
    DECODED_LOG:_maxPerVote::int as maxPerVote,
    DECODED_LOG:_recycled::boolean as recycled,
    DECODED_LOG:_round::int as votium_round,
    DECODED_LOG:_token::string as token,
    contracts.name as token_name,
    contracts.symbol as token_symbol,
    TX_HASH,
    ORIGIN_FROM_ADDRESS

    FROM ethereum.core.ez_decoded_event_logs
    LEFT JOIN ethereum.core.dim_contracts as contracts
    on DECODED_LOG:_token::string = contracts.address
    LEFT JOIN ethereum.price.ez_hourly_token_prices as prices
    ON DECODED_LOG:_token::string = prices.token_address
    AND time_slice(BLOCK_TIMESTAMP::timestamp_ntz, 1, 'HOUR') = prices.HOUR
    WHERE CONTRACT_ADDRESS = lower('{votium_v2}')
    AND event_name = 'NewIncentive'
    {filter_line}
    """
    return query

def fetch(fetch_initial = False):
    print("Fetching... { convex.votium_v2.models }")

    filename = filename_votium_v2
    df = fetch_and_save_data(filename, generate_query, fetch_initial)
    return df
