from app.utilities.utility import (
    pd
)



def get_curve_liquidity_aggs(df):
    df = df[df['balance']> 0]
    df = df.sort_values(['checkpoint_timestamp', 'gauge_name', 'symbol'])
    # Aggregate info down to particular gauges
    df_aggs = df.groupby([
                # 'final_lock_time',
                'checkpoint_timestamp',
                'checkpoint_id',
                'block_timestamp',
                'gauge_addr',
                'gauge_name',
                'gauge_symbol',
                'pool_addr',
            ]).agg(
            total_vote_power=pd.NamedAgg(column='total_vote_power', aggfunc='mean'),
            total_balance=pd.NamedAgg(column='balance', aggfunc=sum),
            total_balance_usd=pd.NamedAgg(column='balance_usd', aggfunc=sum),
            tradable_assets=pd.NamedAgg(column='symbol', aggfunc=list),
            ).reset_index()
    df_aggs['liquidity_over_votes'] = df_aggs['total_balance'] / df_aggs['total_vote_power']
    df_aggs['liquidity_usd_over_votes'] = df_aggs['total_balance_usd'] / df_aggs['total_vote_power']
    df_aggs = df_aggs.sort_values(['block_timestamp', 'total_vote_power'])
    return df_aggs