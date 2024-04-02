from app.data.flipside_api_helper import fetch_and_save_data
from app.data.reference import filename_curve_locker


def generate_query(min_hour=None):

    if min_hour:
        filter_line = f"AND HOUR >= '{min_hour}'"
    else:
        filter_line = ""

    query = f""" 
    SELECT *
    FROM ethereum.price.ez_hourly_token_prices
    WHERE TOKEN_ADDRESS = lower('0xd533a949740bb3306d119cc777fa900ba034cd52')
    ORDER BY HOUR DESC
    {filter_line}
    """
    return query


def fetch(fetch_initial = False):
    filename = filename_curve_locker
    df = fetch_and_save_data(filename, generate_query, fetch_initial)
    return df


