from app.utilities.utility import pd, get_date_obj, nullify_list



def format_df(df):
    key_list = df.keys()

    if 'block_timestamp' in key_list:
        df['block_timestamp']       = df['block_timestamp'].apply(get_date_obj)

    if 'proposal_start' in key_list:
        df['proposal_start']        =df['proposal_start'].apply(get_date_obj)

    if 'this_epoch' in key_list:
        df['this_epoch']        =df['this_epoch'].apply(get_date_obj)

    if 'current_locked' in key_list:
        df['current_locked']       = df['current_locked'].astype(float)

    if 'lock_count' in key_list:
        df['lock_count']       = df['lock_count'].astype(float)

    if 'staked_balance' in key_list:
        df['staked_balance']       = df['staked_balance'].astype(float)
    if '' in df.keys():
        df = df.drop(columns=[''])
    return df

def bind_snapshot_context_to_delegations(df_snapshot_votes, aggregate_delegates):
    df = pd.merge(
        df_snapshot_votes,
        aggregate_delegates,
        how='left',
        left_on=['proposal_title', 'proposal_start', 'voter'],
        right_on=['proposal_title', 'proposal_start', 'delegate' ]
    ).reset_index()
    df['delegators'] = df['delegators'].apply(lambda x: nullify_list(x))
    df['known_delegators'] = df['known_delegators'].apply(lambda x: nullify_list(x, True))
    return df
