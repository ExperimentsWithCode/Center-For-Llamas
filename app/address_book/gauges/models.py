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


print_mode("Loading... { address_book.gauges.models }")


def unique_to_df(df_series, key = None):
    addr_list = list(df_series.unique())
    base_map = {'gauge_addr': addr_list}
    if key:
        val = [True] * len(addr_list) 
        base_map[key] = val
    return pd.DataFrame(base_map)

def gauge_name_helper(gauge_registry, gauge_addr):
    gauge_name = gauge_registry.get_gauge_name(gauge_addr)
    if gauge_addr:
        return gauge_name
    else:
        return '' 
    
def monster_mash():
    try:
        gauge_registry = app.config['gauge_registry']
        df_curve_gauge_registry = app.config['df_curve_gauge_registry']

        # Curve
        df_all_votes = app.config['df_all_votes']
        df_curve_liquidity = app.config['df_curve_liquidity']

        # Snapshot
        df_snapshot_convex = app.config['df_convex_snapshot_vote_choice']
        df_snapshot_stakedao = app.config['df_stakedao_snapshot_vote_choice'] 

        # Votium
        df_votium = app.config['df_votium']
        df_votium_v2 = app.config['df_votium_v2']

    except:
        from app.curve.gauges.models import gauge_registry, df_curve_gauge_registry

        # Curve
        from app.curve.gauge_votes.models import df_all_votes
        from app.curve.liquidity.models import df_curve_liquidity

        # Snapshot
        from app.convex.snapshot.models import df_convex_snapshot_vote_choice as df_snapshot_convex
        from app.stakedao.snapshot.models import df_stakedao_snapshot_vote_choice as df_snapshot_stakedao

        # Votium
        # from app.convex.votium_bounties.models import df_votium_bounty_formatted as df_votium
        from app.convex.votium_bounties_v2.models import df_votium_v2


    df_all_votes = unique_to_df(df_all_votes.gauge_addr, 'vecrv_votes')
    curve_liquidity = unique_to_df(df_curve_liquidity.gauge_addr, 'curve_liquidity')   # maybe voter instead?

    convex_snapshot = unique_to_df(df_snapshot_convex.gauge_addr, 'convex_snapshot')
    stakedao_snapshot = unique_to_df(df_snapshot_stakedao.gauge_addr, 'stakedao_snapshot')
    # df_votium = unique_to_df(df_votium.gauge_addr, 'df_votium')
    df_votium_v2 = unique_to_df(df_votium_v2.gauge_addr, 'votium_v2')


    df_roles = pd.concat([
        df_all_votes,
        curve_liquidity,
        convex_snapshot,
        stakedao_snapshot,
        # df_votium,
        df_votium_v2,
    ])

    # df_roles['gauge_name'] = df_roles.apply(
    #     lambda x: gauge_registry.get_gauge_name(x['gauge_addr']), 
    #     axis=1)

    df_roles = df_roles.groupby([

                # 'final_lock_time',
                # 'gauge_name',
                'gauge_addr',
            ]).agg(
            vecrv_votes=pd.NamedAgg(column='vecrv_votes', aggfunc=sum),
            curve_liquidity=pd.NamedAgg(column='curve_liquidity', aggfunc=sum),
            convex_snapshot=pd.NamedAgg(column='convex_snapshot', aggfunc=sum),
            stakedao_snapshot=pd.NamedAgg(column='stakedao_snapshot', aggfunc=sum),
            # df_votium=pd.NamedAgg(column='df_votium', aggfunc=sum),
            votium_v2=pd.NamedAgg(column='votium_v2', aggfunc=sum),
            ).reset_index()

    df_curve_gauge_registry_2 = pd.merge(
        df_curve_gauge_registry, 
        df_roles, 
        how='left', 
        on = ['gauge_addr'],
        ) 

    try:
        app.config['df_curve_gauge_registry'] = df_curve_gauge_registry_2

    except:
        print_mode("could not register in app.config\n\Address Book Gauges")
    
    return df_roles

def format_df(df):
    # pass
    return df

# def get_df(filename, location):
#     df = csv_to_df(filename, location)
#     df = format_df(df)
#     return df

# df_roles = get_df(filename_actors, MODELS_FOLDER_PATH)
df_gauge_book = monster_mash()



