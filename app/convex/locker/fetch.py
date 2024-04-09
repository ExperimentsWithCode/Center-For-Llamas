from app.data.flipside_api_helper import fetch_and_save_data
from app.data.reference import filename_convex_locker 


def generate_query(min_block_timestamp=None):
    cxv_locker = '0x72a19342e8F1838460eBFCCEf09F6585e32db86E'

    if min_block_timestamp:
        filter_line = f"AND BLOCK_TIMESTAMP >= '{min_block_timestamp}'"
    else:
        filter_line = ""

    query = f"""
    with staked as (
    SELECT 
    (cast(DECODED_LOG:_boostedAmount::string as int) * pow(10,-18))  as boosted_amount,
    DECODED_LOG:_epoch::int as _epoch,
    (cast(DECODED_LOG:_lockedAmount::string as int)  * pow(10,-18)) as locked_amount,
    (cast(DECODED_LOG:_paidAmount::string as int)  * pow(10,-18)) as paid_amount,
    lower(DECODED_LOG:_user::string) as user,
    BLOCK_TIMESTAMP as block_timestamp,
    EVENT_NAME as event_name,
    TX_HASH as tx_hash

    FROM ethereum.core.ez_decoded_event_logs
    WHERE CONTRACT_ADDRESS =  lower('{cxv_locker}')
    AND EVENT_NAME = 'Staked'
    {filter_line}
    ORDER BY block_timestamp desc

    ),
    withdrawn as (
    SELECT 
    (cast(DECODED_LOG:_amount::string as int) * pow(10,-18)) as withdrawn_amount,
    DECODED_LOG:_relocked::boolean as relocked,
    lower(DECODED_LOG:_user::string) as user,
    BLOCK_TIMESTAMP as block_timestamp,
    EVENT_NAME as event_name,
    TX_HASH as tx_hash
    FROM ethereum.core.ez_decoded_event_logs
    WHERE CONTRACT_ADDRESS =  lower('{cxv_locker}')
    AND EVENT_NAME = 'Withdrawn'
    {filter_line}
    ORDER BY block_timestamp desc


    )
    SELECT 
    block_timestamp,
    event_name,
    user, 
    _epoch,
    locked_amount,
    boosted_amount, 
    paid_amount,
    0 as withdrawn_amount,
    FALSE as relocked,
    tx_hash
    FROM staked
    UNION ALL
    SELECT 
    block_timestamp,
    event_name,
    user, 
    0 as_epoch,
    0 as locked_amount,
    0 as boosted_amount, 
    0 as paid_amount,
    withdrawn_amount,
    relocked,
    tx_hash
    FROM withdrawn
    """
    return query

def fetch(fetch_initial = False):
    print("Fetching... { convex.locker.models }")

    filename = filename_convex_locker
    df = fetch_and_save_data(filename, generate_query, fetch_initial)
    return df

