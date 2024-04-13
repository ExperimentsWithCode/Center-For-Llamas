from flask import current_app as app

from app.data.reference import filename_actors, known_large_market_actors

from app.data.local_storage import (
    pd,
    write_dataframe_csv,
    )

from app.utilities.utility import print_mode

def monster_mash():
    try:
        df_curve_vecrv = app.config['df_curve_gauge_registry']

        df_snapshot = app.config['df_snapshot']

        df_snapshot_stakedao = app.config['df_snapshot'] 

        df_vote_aggregates = app.config['df_vote_aggregates']

        df_votium_v2 = app.config['df_votium_v2']

    except:
        from app.curve.gauges.models import df_curve_gauge_registry
        from app.curve.liquidity.models import df_curve_liquidity_aggregates

        from app.convex.snapshot.models import df_snapshot

        from app.stakedao.snapshot.models import df_snapshot as df_snapshot_stakedao

        from app.convex.votium_bounties.models import df_vote_aggregates
        from app.convex.votium_bounties_v2.models import df_votium_v2



    curve_gauges = df_curve_gauge_registry.gauge_addr.unique()

    convex_snapshot_votes = df_snapshot.gauge_addr.unique()

    stakedao_snapshot_votes = df_snapshot_stakedao.gauge_addr.unique()
    votium_bounties = df_vote_aggregates.gauge_addr.unique()
    votium_v2_bounties = df_votium_v2.gauge_addr.unique()



    all_addresses = list(curve_gauges) + list(convex_snapshot_votes)
    all_addresses += list(convex_snapshot_votes) + list(stakedao_snapshot_votes) 
    all_addresses += list(votium_bounties) + list(votium_v2_bounties) 

    unique_address_list = list(set(all_addresses))
    
    output = []
    for address in unique_address_list:
        row = {
            'address': address,
            'known_as': known_large_market_actors[address] if address in known_large_market_actors else '_',
            'curve_gauges': True if address in curve_gauges else False,
            'convex_snapshot_votes': True if address in convex_snapshot_votes else False,
            'stakedao_snapshot_votes': True if address in stakedao_snapshot_votes else False,
            'votium_bounties': True if address in votium_bounties else False,
            'votium_v2_bounties': True if address in votium_v2_bounties else False,


            
        }
        output.append(row)

    return pd.json_normalize(output)


def process_and_save():


    print_mode("Processing... { AddressBook.actors.models }")
    df = monster_mash()

    write_dataframe_csv(filename_actors, df, 'processed')

    try:
        # app.config['df_active_votes'] = df_active_votes
        app.config['df_actors'] = df
    except:
        print_mode("could not register in app.config\n\tVotium v2")
    return {
        # 'df_active_votes': df_active_votes,
        'df_actors': df,
    }