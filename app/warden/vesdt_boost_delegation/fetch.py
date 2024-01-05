from app.data.flipside_api_helper import fetch_and_save_data
from app.data.reference import filename_warden_vesdt_boost_delegation 

def generate_query(min_block_timestamp=None):
    cxv_locker = '0x72a19342e8F1838460eBFCCEf09F6585e32db86E'

    if min_block_timestamp:
        filter_line = f"AND BLOCK_TIMESTAMP >= '{min_block_timestamp}'"
    else:
        filter_line = ""

    query = f"""
    SELECT
    BLOCK_TIMESTAMP as block_timestamp,
    (TO_NUMBER(DECODED_LOG:amount::string) / POW(10,18)) as amount,

    DECODED_LOG:delegator::string as delegator,
    DECODED_LOG:expiryTime::int as expiry_time,
    (TO_NUMBER(DECODED_LOG:paidFeeAmount::string) / POW(10,18)) as paid_fee_amount,
    DECODED_LOG:price::int as price,
    DECODED_LOG:receiver::string as receiver,
    DECODED_LOG:tokenId::int as token_id,
    TX_HASH as tx_hash

    FROM ethereum.core.ez_decoded_event_logs
    WHERE CONTRACT_ADDRESS = lower('0x469C7cEd68487102161deF8e05dc071205c87699')
    AND EVENT_NAME = 'BoostPurchase'
    {filter_line}

    """
    return query

def fetch(fetch_initial = False):
    print("Fetching... { convex.locker.models }")

    filename = filename_warden_vesdt_boost_delegation
    df = fetch_and_save_data(filename, generate_query, fetch_initial)
    return df

