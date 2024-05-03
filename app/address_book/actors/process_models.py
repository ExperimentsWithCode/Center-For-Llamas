from flask import current_app as app

from app.data.reference import filename_actors, known_large_market_actors

from app import MODELS_FOLDER_PATH, RAW_FOLDER_PATH
from app.data.local_storage import (
    pd,
    df_to_csv,
    )

from app.utilities.utility import print_mode

# def monster_mash():
#     try:
#         df_curve_vecrv = app.config['df_curve_vecrv']
#         df_all_votes = app.config['df_all_votes']

#         df_snapshot = app.config['df_convex_snapshot_vote_choice']
#         df_convex_delegations = app.config['df_convex_delegations']
#         df_locker = app.config['df_locker']

#         df_snapshot_stakedao = app.config['df_stakedao_snapshot_vote_choice'] 
#         # df_stakedao_delegations = # app.config['df_stakedao_delegations']
#         df_stakedao_vesdt = app.config['df_stakedao_vesdt']

#         df_stakedao_sdcrv = app.config['df_stakedao_sdcrv']
#         df_stakedao_sdcrv = app.config['df_stakedao_delegations']

#     except:
#         from app.curve.locker.models import df_curve_vecrv
#         from app.curve.gauge_votes.models import df_all_votes

#         from app.convex.snapshot.models import df_snapshot
#         from app.convex.delegations.models import df_convex_delegations
#         from app.convex.locker.models import df_locker

#         from app.stakedao.snapshot.models import df_snapshot as df_snapshot_stakedao
#         # from app.stakedao.delegations.models import df_stakedao_delegations
#         from app.stakedao.locker.models import df_stakedao_vesdt

#         from app.stakedao.staked_sdcrv.models import df_stakedao_sdcrv
#         from app.stakedao.staked_sdcrv.models import df_stakedao_sdcrv
#         from app.stakedao.delegations.models import df_stakedao_delegations


#     curve_vecrv_lockers = df_curve_vecrv.provider.unique()
#     curve_voters = df_all_votes.user.unique()   # maybe voter instead?

#     convex_snapshot_voters = df_snapshot.voter.unique()
#     convex_delegators = df_convex_delegations.delegator.unique()
#     convex_delegates = df_convex_delegations.delegate.unique()
#     convex_vlcvx_lockers = df_locker.user.unique()

#     stakedao_snapshot_voters = df_snapshot_stakedao.voter.unique()
#     stakedao_vesdt_lockers = df_stakedao_vesdt.provider.unique()
#     stakedao_sdcrv_stakers = df_stakedao_sdcrv.provider.unique()
#     stakedao_delegators = df_stakedao_delegations.delegator.unique()
#     stakedao_delegates = df_stakedao_delegations.delegate.unique()


#     all_addresses = list(curve_vecrv_lockers) + list(curve_voters)
#     all_addresses += list(convex_snapshot_voters) + list(convex_delegates) +list(convex_delegators) + list(convex_vlcvx_lockers)
#     all_addresses += list(stakedao_snapshot_voters) + list(stakedao_vesdt_lockers) +list(stakedao_sdcrv_stakers)

#     unique_address_list = list(set(all_addresses))
    
#     output = []
#     for address in unique_address_list:
#         row = {
#             'address': address,
#             'known_as': known_large_market_actors[address] if address in known_large_market_actors else '_',
#             'curve_vecrv_locker': True if address in curve_vecrv_lockers else False,
#             'curve_voters': True if address in curve_voters else False,
            
#             'convex_snapshot_voter': True if address in convex_snapshot_voters else False,
#             'convex_vlcvx_locker': True if address in convex_vlcvx_lockers else False,
#             'convex_delegator': True if address in convex_delegators else False,
#             'convex_delegate': True if address in convex_delegates else False,
            
#             'stakedao_snapshot_voter': True if address in stakedao_snapshot_voters else False,
#             'stakedao_sdcrv_staker': True if address in stakedao_sdcrv_stakers else False,
#             'stakedao_vesdt_locker': True if address in stakedao_vesdt_lockers else False,
#             'stakedao_delegator': True if address in stakedao_delegators else False,
#             'stakedao_delegate': True if address in stakedao_delegates else False,
#         }
#         output.append(row)

#     return pd.json_normalize(output)


def unique_to_df(df_series, key = None):
    addr_list = list(df_series.unique())
    base_map = {'address': addr_list}
    if key:
        val = [True] * len(addr_list) 
        base_map[key] = val
    return base_map

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
        curve_vecrv_lockers['address'],
        curve_voters['address'],
        convex_snapshot_voters['address'],
        convex_delegators['address'],
        convex_delegates['address'],
        convex_vlcvx_lockers['address'],
        stakedao_snapshot_voters['address'],
        stakedao_vesdt_lockers['address'],
        stakedao_sdcrv_stakers['address'],
        stakedao_delegators['address'],
        stakedao_delegates['address'],
    ])

    return df_roles.groupby([
                # 'final_lock_time',
                'address',
            ]).agg(
            curve_vecrv_locker=pd.NamedAgg(column='curve_vecrv_locker', aggfunc=sum).astype(float),
            curve_voters=pd.NamedAgg(column='curve_voters', aggfunc=sum).astype(float),
            convex_snapshot_voter=pd.NamedAgg(column='convex_snapshot_voter', aggfunc=sum).astype(float),
            convex_delegator=pd.NamedAgg(column='convex_delegator', aggfunc=sum).astype(float),
            convex_delegate=pd.NamedAgg(column='convex_delegate', aggfunc=sum).astype(float),
            convex_vlcvx_locker=pd.NamedAgg(column='convex_vlcvx_locker', aggfunc=sum).astype(float),
            stakedao_snapshot_voter=pd.NamedAgg(column='stakedao_snapshot_voter', aggfunc=sum).astype(float),
            stakedao_sdcrv_staker=pd.NamedAgg(column='stakedao_sdcrv_staker', aggfunc=sum).astype(float),
            stakedao_vesdt_locker=pd.NamedAgg(column='stakedao_vesdt_locker', aggfunc=sum).astype(float),
            stakedao_delegator=pd.NamedAgg(column='stakedao_delegator', aggfunc=sum).astype(float),
            stakedao_delegate=pd.NamedAgg(column='stakedao_delegate', aggfunc=sum).astype(float),
            ).reset_index()

def process_and_save():


    print_mode("Processing... { AddressBook.actors.models }")
    df = monster_mash()

    df_to_csv(df, filename_actors, MODELS_FOLDER_PATH)

    try:
        # app.config['df_active_votes'] = df_active_votes
        app.config['df_roles'] = df
    except:
        print_mode("could not register in app.config\n\tVotium v2")
    return {
        # 'df_active_votes': df_active_votes,
        'df_roles': df,
    }