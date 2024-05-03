from app.utilities.utility import pd, get_date_obj


def format_df(df):
    df['choice_index'] = df['choice_index'].astype(int)
    df['voting_weight'] = df['voting_weight'].astype(float)
    df['total_weight'] = df['total_weight'].astype(float)
    df['choice_percent'] = df['choice_percent'].astype(float)
    df['available_power'] = df['available_power'].astype(float)
    df['choice_power'] = df['choice_power'].astype(float)
    df['valid'] = df['valid'].astype(bool)
    df['checkpoint_timestamp'] = pd.to_datetime(df['checkpoint_timestamp'])
    df['proposal_start'] = df['proposal_start'].apply(get_date_obj)
    df['proposal_end'] = df['proposal_end'].apply(get_date_obj)

    return df
