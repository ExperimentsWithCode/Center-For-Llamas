from app.utilities.utility import (
    pd
)

def sort(df=[], target='block_timestamp'):
    if len(df) == 0:
        return df
    return df.sort_values([target], axis = 0, ascending = True)

def get_stakedao_sdcrv_agg(df_stakedao_sdcrv):
    processed_agg = df_stakedao_sdcrv[['date', 'balance_delta']].groupby([
            'date'
        ]).agg(
        balance_delta=pd.NamedAgg(column='balance_delta', aggfunc=sum),
    ).reset_index()
    processed_agg = sort(processed_agg, 'date')
    processed_agg['total_staked_balance'] = processed_agg['balance_delta'].transform(pd.Series.cumsum)
    return processed_agg


def get_stakedao_sdcrv_agg_known(df_stakedao_sdcrv):
    processed_known = df_stakedao_sdcrv[['known_as', 'date', 'balance_delta']].groupby([
            'date', 'known_as'
        ]).agg(
        balance_delta=pd.NamedAgg(column='balance_delta', aggfunc=sum),
    ).reset_index()

    processed_known = sort(processed_known, 'date')
    processed_known['staked_balance'] = processed_known.groupby('known_as')['balance_delta'].transform(pd.Series.cumsum)
    # set end value of current balance w/o delta from last delta

    return processed_known