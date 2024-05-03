from flask import current_app as app
from app.data.reference import filename_actors, known_large_market_actors

from app import MODELS_FOLDER_PATH

from app.data.local_storage import (
    pd,
    # read_json,
    # read_csv,
    # write_dataframe_csv,
    # write_dfs_to_xlsx,
    csv_to_df
    )


from app.utilities.utility import (
    # get_period_direct, 
    # get_period_end_date, 
    get_date_obj, 
    get_dt_from_timestamp,
    nullify_amount,
    print_mode
    # shift_time_days,
    # df_remove_nan
    

)


print_mode("Loading... { address_book.actors.models }")


def unique_to_df(df_series, key = None):
    addr_list = list(df_series.unique())
    base_map = {'address': addr_list}
    if key:
        val = [True] * len(addr_list) 
        base_map[key] = val
    return pd.DataFrame(base_map)

def known_as_helper(address):
    if address in known_large_market_actors:
        return known_large_market_actors[address]
    else:
        return '_' 
    
def monster_mash():
    try:
        df_curve_vecrv = app.config['df_curve_vecrv']
        df_all_votes = app.config['df_all_votes']

        df_snapshot = app.config['df_convex_snapshot_vote_choice']
        df_convex_delegations = app.config['df_convex_delegations']
        df_locker = app.config['df_locker']

        df_snapshot_stakedao = app.config['df_stakedao_snapshot_vote_choice'] 
        # df_stakedao_delegations = # app.config['df_stakedao_delegations']
        df_stakedao_vesdt = app.config['df_stakedao_vesdt']

        df_stakedao_sdcrv = app.config['df_stakedao_sdcrv']
        df_stakedao_sdcrv = app.config['df_stakedao_delegations']

    except:
        from app.curve.locker.models import df_curve_vecrv
        from app.curve.gauge_votes.models import df_all_votes

        from app.convex.snapshot.models import df_convex_snapshot_vote_choice as df_snapshot
        from app.convex.delegations.models import df_convex_delegations
        from app.convex.locker.models import df_locker

        from app.stakedao.snapshot.models import df_stakedao_snapshot_vote_choice as df_snapshot_stakedao
        # from app.stakedao.delegations.models import df_stakedao_delegations
        from app.stakedao.locker.models import df_stakedao_vesdt

        from app.stakedao.staked_sdcrv.models import df_stakedao_sdcrv
        from app.stakedao.staked_sdcrv.models import df_stakedao_sdcrv
        from app.stakedao.delegations.models import df_stakedao_delegations


    curve_vecrv_lockers = unique_to_df(df_curve_vecrv.provider, 'curve_vecrv_locker')
    curve_voters = unique_to_df(df_all_votes.user, 'curve_voters')   # maybe voter instead?

    convex_snapshot_voters = unique_to_df(df_snapshot.voter, 'convex_snapshot_voter')
    convex_delegators = unique_to_df(df_convex_delegations.delegator, 'convex_delegator')
    convex_delegates = unique_to_df(df_convex_delegations.delegate, 'convex_delegate')
    convex_vlcvx_lockers = unique_to_df(df_locker.user, 'convex_vlcvx_locker')

    stakedao_snapshot_voters = unique_to_df(df_snapshot_stakedao.voter, 'stakedao_snapshot_voter')
    stakedao_vesdt_lockers = unique_to_df(df_stakedao_vesdt.provider, 'stakedao_sdcrv_staker')
    stakedao_sdcrv_stakers = unique_to_df(df_stakedao_sdcrv.provider, 'stakedao_vesdt_locker')
    stakedao_delegators = unique_to_df(df_stakedao_delegations.delegator, 'stakedao_delegator')
    stakedao_delegates = unique_to_df(df_stakedao_delegations.delegate, 'stakedao_delegate')



    df_roles = pd.concat([
        curve_vecrv_lockers,
        curve_voters,
        convex_snapshot_voters,
        convex_delegators,
        convex_delegates,
        convex_vlcvx_lockers,
        stakedao_snapshot_voters,
        stakedao_vesdt_lockers,
        stakedao_sdcrv_stakers,
        stakedao_delegators,
        stakedao_delegates,
    ])


    df_roles['known_as'] = df_roles.apply(
        lambda x: known_as_helper(x['address']), 
        axis=1)
    return df_roles.groupby([

                # 'final_lock_time',
                'known_as',
                'address',
            ]).agg(
            curve_vecrv_locker=pd.NamedAgg(column='curve_vecrv_locker', aggfunc=sum),
            curve_voters=pd.NamedAgg(column='curve_voters', aggfunc=sum),
            convex_snapshot_voter=pd.NamedAgg(column='convex_snapshot_voter', aggfunc=sum),
            convex_delegator=pd.NamedAgg(column='convex_delegator', aggfunc=sum),
            convex_delegate=pd.NamedAgg(column='convex_delegate', aggfunc=sum),
            convex_vlcvx_locker=pd.NamedAgg(column='convex_vlcvx_locker', aggfunc=sum),
            stakedao_snapshot_voter=pd.NamedAgg(column='stakedao_snapshot_voter', aggfunc=sum),
            stakedao_sdcrv_staker=pd.NamedAgg(column='stakedao_sdcrv_staker', aggfunc=sum),
            stakedao_vesdt_locker=pd.NamedAgg(column='stakedao_vesdt_locker', aggfunc=sum),
            stakedao_delegator=pd.NamedAgg(column='stakedao_delegator', aggfunc=sum),
            stakedao_delegate=pd.NamedAgg(column='stakedao_delegate', aggfunc=sum),
            ).reset_index()

def format_df(df):
    # pass
    return df

# def get_df(filename, location):
#     df = csv_to_df(filename, location)
#     df = format_df(df)
#     return df

# df_roles = get_df(filename_actors, MODELS_FOLDER_PATH)
df_roles = monster_mash()

try:
    app.config['df_roles'] = df_roles

except:
    print_mode("could not register in app.config\n\Address Book Actors")

