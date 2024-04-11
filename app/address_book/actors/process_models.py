from flask import current_app as app

from app.data.reference import filename_actors, known_large_market_actors

from app.data.local_storage import (
    pd,
    write_dataframe_csv,
    )

def monster_mash():
    try:
        df_curve_vecrv = app.config['df_curve_vecrv']
        df_all_votes = app.config['df_all_votes']

        df_snapshot = app.config['df_snapshot']
        df_convex_delegations = app.config['df_convex_delegations']
        df_locker = app.config['df_locker']

        df_snapshot_stakedao = app.config['df_snapshot'] 
        # df_stakedao_delegations = # app.config['df_stakedao_delegations']
        df_stakedao_vesdt = app.config['df_stakedao_vesdt']

        df_stakedao_sdcrv = app.config['df_stakedao_sdcrv']
        df_stakedao_sdcrv = app.config['df_stakedao_delegations']

    except:
        from app.curve.locker.models import df_curve_vecrv
        from app.curve.gauge_votes.models import df_all_votes

        from app.convex.snapshot.models import df_snapshot
        from app.convex.delegations.models import df_convex_delegations
        from app.convex.locker.models import df_locker

        from app.stakedao.snapshot.models import df_snapshot as df_snapshot_stakedao
        # from app.stakedao.delegations.models import df_stakedao_delegations
        from app.stakedao.locker.models import df_stakedao_vesdt

        from app.stakedao.staked_sdcrv.models import df_stakedao_sdcrv
        from app.stakedao.staked_sdcrv.models import df_stakedao_sdcrv
        from app.stakedao.delegations.models import df_stakedao_delegations


    curve_vecrv_lockers = df_curve_vecrv.provider.unique()
    curve_voters = df_all_votes.user.unique()   # maybe voter instead?

    convex_snapshot_voters = df_snapshot.voter.unique()
    convex_delegators = df_convex_delegations.delegator.unique()
    convex_delegates = df_convex_delegations.delegate.unique()
    convex_vlcvx_lockers = df_locker.user.unique()

    stakedao_snapshot_voters = df_snapshot_stakedao.voter.unique()
    stakedao_vesdt_lockers = df_stakedao_vesdt.provider.unique()
    stakedao_sdcrv_stakers = df_stakedao_sdcrv.provider.unique()
    stakedao_delegators = df_stakedao_delegations.delegator.unique()
    stakedao_delegates = df_stakedao_delegations.delegate.unique()


    all_addresses = list(curve_vecrv_lockers) + list(curve_voters)
    all_addresses += list(convex_snapshot_voters) + list(convex_delegates) +list(convex_delegators) + list(convex_vlcvx_lockers)
    all_addresses += list(stakedao_snapshot_voters) + list(stakedao_vesdt_lockers) +list(stakedao_sdcrv_stakers)

    unique_address_list = list(set(all_addresses))
    
    output = []
    for address in unique_address_list:
        row = {
            'address': address,
            'known_as': known_large_market_actors[address] if address in known_large_market_actors else '_',
            'curve_vecrv_locker': True if address in curve_vecrv_lockers else False,
            'curve_voters': True if address in curve_voters else False,
            
            'convex_snapshot_voter': True if address in convex_snapshot_voters else False,
            'convex_vlcvx_locker': True if address in convex_vlcvx_lockers else False,
            'convex_delegator': True if address in convex_delegators else False,
            'convex_delegate': True if address in convex_delegates else False,
            
            'stakedao_snapshot_voter': True if address in stakedao_snapshot_voters else False,
            'stakedao_sdcrv_staker': True if address in stakedao_sdcrv_stakers else False,
            'stakedao_vesdt_locker': True if address in stakedao_vesdt_lockers else False,
            'stakedao_delegator': True if address in stakedao_delegators else False,
            'stakedao_delegate': True if address in stakedao_delegates else False,
        }
        output.append(row)

    return pd.json_normalize(output)


def process_and_save():
    try:
    from config import activate_print_mode
except:
    activate_print_mode = False

if activate_print_mode:
    print("Processing... { AddressBook.actors.models }")
    df = monster_mash()

    write_dataframe_csv(filename_actors, df, 'processed')

    try:
        # app.config['df_active_votes'] = df_active_votes
        app.config['df_actors'] = df
    except:
        print("could not register in app.config\n\tVotium v2")
    return {
        # 'df_active_votes': df_active_votes,
        'df_actors': df,
    }