votium_bounty_query = f"""

"""


from app.data.flipside_api_helper import fetch_and_save_data
from app.data.reference import filename_votium_v1 


def generate_query(min_block_timestamp=None):
    cxv_locker = '0x72a19342e8F1838460eBFCCEf09F6585e32db86E'

    if min_block_timestamp:
        filter_line = f"AND BLOCK_TIMESTAMP >= '{min_block_timestamp}'"
    else:
        filter_line = "AND BLOCK_TIMESTAMP >= '2023-01-01 00:00:59.000'"

    query = f"""
SELECT 
  EVENT_NAME,
  TX_HASH,
  DECODED_LOG:_choiceIndex::int as choice_index,
  DECODED_LOG:_amount::int / pow(10,18) as amount,
  DECODED_LOG:_proposal::string as proposal_id,
  DECODED_LOG:_token::string as bounty_token_address,
  ORIGIN_FROM_ADDRESS,
  BLOCK_TIMESTAMP as block_timestamp,
  PRICE as price,
  price * amount as bounty_value,
  contracts.NAME as token_name,
  contracts.SYMBOL as token_symbol
FROM ethereum.core.ez_decoded_event_logs as logs

LEFT JOIN ethereum.price.ez_hourly_token_prices as prices
ON logs.DECODED_LOG:_token = prices.token_address
AND time_slice(logs.BLOCK_TIMESTAMP::timestamp_ntz, 1, 'HOUR') = prices.HOUR

LEFT JOIN ethereum.core.dim_contracts as contracts
ON logs.DECODED_LOG:_token = contracts.ADDRESS

WHERE CONTRACT_ADDRESS= lower('0x19bbc3463dd8d07f55438014b021fb457ebd4595')

AND EVENT_NAME = 'Bribed'
{filter_line}

ORDER BY block_timestamp
    """
    return query

def fetch(fetch_initial = False):
    print("Fetching... { convex.votium_v1.models }")

    filename = filename_votium_v1
    df = fetch_and_save_data(filename, generate_query, fetch_initial)
    return df

