from app.data.flipside_api_helper import fetch_and_save_data
from app.data.reference import filename_curve_locker


def generate_query(min_block_timestamp=None):
    curve_locker_address = '0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2'

    if min_block_timestamp:
        filter_line = f"AND BLOCK_TIMESTAMP > '{min_block_timestamp}'"
    else:
        filter_line = ""

    query = f"""SELECT 
    *,
    WEEK(BLOCK_TIMESTAMP) as WEEK_NUMBER,
    DAYOFWEEK(BLOCK_TIMESTAMP) as WEEK_DAY

    FROM ethereum.core.ez_decoded_event_logs
    WHERE CONTRACT_ADDRESS = lower('{curve_locker_address}')
    {filter_line}

    """
    return query


def fetch(fetch_initial = False):
    filename = filename_curve_locker
    df = fetch_and_save_data(filename, generate_query, fetch_initial)
    return df
