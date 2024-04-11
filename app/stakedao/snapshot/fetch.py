from app.data.flipside_api_helper import fetch_and_save_data
from app.data.reference import filename_stakedao_curve_snapshot 
from app.utilities.utility import print_mode

def generate_query(min_block_timestamp=None):
    if min_block_timestamp:
        filter_line = f"AND VOTE_TIMESTAMP >= '{min_block_timestamp}'"
    else:
        filter_line = "AND VOTE_TIMESTAMP > '2022-12-20 00:00:00.000'"

    query = f"""
    SELECT 
        PROPOSAL_ID, 
        PROPOSAL_START_TIME, 
        PROPOSAL_END_TIME, 
        PROPOSAL_TITLE, 
        PROPOSAL_AUTHOR,
        VOTE_OPTION,
        VOTING_POWER,
        VOTE_TIMESTAMP,
        QUORUM,
        CHOICES,
        VOTING_PERIOD,
        NETWORK,
        SPACE_ID,
        VOTER,
        ADDRESS_NAME,
        LABEL_TYPE, 
        LABEL_SUBTYPE,
        LABEL
    FROM external.snapshot.ez_snapshot as SNAPSHOT
    LEFT JOIN ethereum.core.dim_labels LABELS
    ON SNAPSHOT.VOTER = LABELS.ADDRESS
    WHERE SPACE_ID = 'sdcrv.eth' 
    AND (PROPOSAL_TITLE LIKE 'Gauge vote - CRV%'
    OR
    PROPOSAL_TITLE LIKE 'Gauge vote CRV%'
    )
    {filter_line}

    """
    
    # WHERE SPACE_ID = '{space_id}' 
    # AND PROPOSAL_TITLE LIKE '{target}'
    # {filter_line}
    # """
    return query

def fetch(fetch_initial = False):
    print_mode("Fetching... { stakedao.snapshot_curve_votes.models }")

    filename = filename_stakedao_curve_snapshot
    df = fetch_and_save_data(filename, generate_query, fetch_initial, 'vote_timestamp')
    return df
