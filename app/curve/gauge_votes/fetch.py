from app.data.flipside_api_helper import fetch_and_save_data
from app.data.reference import filename_curve_gauge_votes

def generate_query(min_block_timestamp=None):
    curve_voter_address = '0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB'

    if min_block_timestamp:
        filter_line = f"AND BLOCK_TIMESTAMP > '{min_block_timestamp}'"
    else:
        filter_line = ""

    query = f"""SELECT 
        SYMBOL, 
        NAME, 
        WEEK(BLOCK_TIMESTAMP) as WEEK_NUMBER,
        DAYOFWEEK(BLOCK_TIMESTAMP) as WEEK_DAY,
        DECODED_LOG,
        TX_HASH,
        BLOCK_TIMESTAMP

    FROM ethereum.core.ez_decoded_event_logs LOGS
    LEFT JOIN ethereum.core.dim_contracts CONTRACT
    ON CONTRACT.address = lower(LOGS.DECODED_LOG:gauge_addr::string)
    WHERE CONTRACT_ADDRESS = lower('{curve_voter_address}')
    AND EVENT_NAME = 'VoteForGauge'
    {filter_line}
    ORDER BY BLOCK_TIMESTAMP ASC
    """
    return query


def fetch(fetch_initial = False):
    filename = filename_curve_gauge_votes
    df = fetch_and_save_data(filename, generate_query, fetch_initial)
    return df
