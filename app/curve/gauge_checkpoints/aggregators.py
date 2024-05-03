from app.utilities.utility import pd


def get_curve_checkpoint_aggs(df):
    # Aggregate info down to particular gauges
    df_vote_aggs = df.groupby([
                # 'final_lock_time',
                'checkpoint_timestamp',
                'checkpoint_id',
                'gauge_addr',
                'gauge_name',
                'gauge_symbol',
            ]).agg(
            total_vote_power=pd.NamedAgg(column='vote_power', aggfunc=sum),
            total_raw_vote_power=pd.NamedAgg(column='locked_crv', aggfunc=sum),
            total_vote_percent=pd.NamedAgg(column='vote_percent', aggfunc=sum),

            ).reset_index()
    df_vote_aggs = df_vote_aggs.sort_values(['checkpoint_timestamp', 'total_vote_power'])
    return df_vote_aggs