from app.utilities.utility import (
    pd
)



def get_ve_locker_decay_agg(df_vetoken_decay): 
    return df_vetoken_decay.groupby([
            'checkpoint_timestamp',
            'checkpoint_id',
        ]).agg(
            total_locked_balance=pd.NamedAgg(column='total_locked_balance', aggfunc=sum),
            total_effective_locked_balance=pd.NamedAgg(column='total_effective_locked_balance', aggfunc=sum),
        ).reset_index()

def get_ve_locker_agg(df_vetoken): 
    processed_agg = df_vetoken[['checkpoint_id', 'checkpoint_timestamp', 'balance_delta']].groupby([
            'checkpoint_id',
            'checkpoint_timestamp'
        ]).agg(
        balance_delta=pd.NamedAgg(column='balance_delta', aggfunc=sum),
    ).reset_index()
    processed_agg = processed_agg.sort_values('checkpoint_id')
    processed_agg['total_locked_balance'] = processed_agg['balance_delta'].transform(pd.Series.cumsum)
    return processed_agg


def get_ve_locker_agg_known(df_vetoken):
    processed_known = df_vetoken[['known_as', 'checkpoint_id', 'checkpoint_timestamp', 'balance_delta']].groupby([
            'checkpoint_id', 'known_as',
        ]).agg(
        balance_delta=pd.NamedAgg(column='balance_delta', aggfunc=sum),
    ).reset_index()

    processed_known = processed_known.sort_values('checkpoint_id')
    processed_known['locked_balance'] = processed_known.groupby('known_as')['balance_delta'].transform(pd.Series.cumsum)
    # set end value of current balance w/o delta from last delta

    return processed_known