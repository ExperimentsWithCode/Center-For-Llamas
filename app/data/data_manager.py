from app.utilities.utility import timed
from app.snapshot.alt_models import SnapshotAsSource

from app.data.local_storage import (
    read_json,
    read_csv,
    csv_to_df,
    df_to_csv,
)
# from app.data.local_storage import get_cwd
# import pandas as pd

load_initial = False
should_fetch = True

default_bool = True

manager_config = {
    # Curve
    'gauge_to_map': default_bool,
    'curve_locker': default_bool,
    'curve_gauge_votes': default_bool,
    'curve_gauge_rounds': default_bool,

    'curve_liquidity': default_bool, ## New Source Now

    # Convex
    'convex_locker': default_bool,
    'convex_delegations': default_bool,
    'convex_snapshot_curve': default_bool,
    
    # StakeDAO
    'stakedao_delegations': default_bool,
    'stakedao_staked_sdcrv': default_bool,
    'stakedao_locker': default_bool,
    'stakedao_snapshot_curve': default_bool,

    #Votium
    'votium_bounties_v2': default_bool,
    # Warden
    'warden_vesdt_boost_delegation': False,
}

# run['curve_locker'] = True
# run['stakedao_locker'] = True



class Manager():
    def __init__(self,
                manager_config=manager_config,
                should_fetch=should_fetch,
                load_initial = load_initial,
                # Curve Liquidity Focus
                load_cutoff = False,   
                cutoff_value = None,
                human_management = False,
                ):
        self.config = manager_config
        self.should_fetch = should_fetch
        self.load_initial = load_initial
        self.load_liquidity_cutoff = load_cutoff
        self.liquidity_cutoff_value = cutoff_value
        self.human_management = human_management

    def manage(self):
        # Curve
        self.gauge_to_lp_map()
        self.curve_locker()
        self.curve_gauge_votes()
        self.curve_gauge_rounds()
        self.curve_liquidity()
        # Convex
        self.convex_locker()
        self.convex_snapshot_curve()
        self.convex_snapshot_curve_from_snapshot()
        # StakeDAO
        self.stakedao_staked_sdcrv()
        self.stakedao_locker()
        self.stakedao_snapshot_curve()
        self.stakedao_snapshot_curve_from_snapshot()
        # Votium
        self.votium_bounties_v2()

        # Warden

    """
    Curve
    """
    @timed
    def gauge_to_lp_map(self):
        if self.config['gauge_to_map']:   
            from app.curve.gauges.fetch import fetch 
            from app.curve.gauges.process_flipside import process_and_save 
            # from app.curve.gauges.process_flipside import process_and_get 

            return self._helper(fetch, process_and_save, True)
    
    @timed
    def curve_locker(self):
        if self.config['curve_locker']:   
            from app.curve.locker.fetch import fetch 
            from app.curve.locker.process_flipside import process_and_save 

            return self._helper(fetch, process_and_save)
    
    @timed
    def curve_gauge_votes(self):
        if self.config['curve_gauge_votes']:   
            from app.curve.gauge_votes.fetch import fetch 
            from app.curve.gauge_votes.process_flipside import process_and_save 

            return self._helper(fetch, process_and_save)
    
    @timed
    def curve_gauge_rounds(self):
        if self.config['curve_gauge_rounds']:   
            from app.curve.gauge_rounds.process_flipside import process_and_save 

            return self._helper(None, process_and_save)
        
    @timed
    def curve_liquidity(self):
        if self.config['curve_liquidity']:   
            from app.curve.liquidity.liquidity_data_manager import LiquidityManager
            from app.curve.liquidity.process_flipside import process_and_save 
            LiquidityManager(
                self.should_fetch, 
                self.load_initial, 
                self.load_liquidity_cutoff,
                self.liquidity_cutoff_value,
                self.human_management)
            return self._helper(None, process_and_save)
    
    ## NEED LIQUIDITY
    
    """
    Convex
    """
    
    @timed
    def convex_locker(self):
        if self.config['convex_locker']:   
            from app.convex.locker.fetch import fetch 
            from app.convex.locker.process_flipside import process_and_save

            return self._helper(fetch, process_and_save)

    @timed
    def convex_snapshot_curve(self):
        if self.config['convex_snapshot_curve']:   
            from app.convex.snapshot.fetch import fetch 
            # from app.convex.locker.process_flipside import process_and_save

            return self._helper(fetch, None)
        
    @timed
    def convex_snapshot_curve_from_snapshot(self):
        if self.config['convex_snapshot_curve']: 
            if self.should_fetch:
                space_address = 'cvx.eth'
                first = 200
                skip = 0
                target = None
                snapshot = SnapshotAsSource(space_address, first, skip, target )
                snapshot.save_files('convex')

            # from app.convex.snapshot.fetch import fetch 
            # from app.convex.locker.process_flipside import process_and_save

            # return self._helper(fetch, None)
    # @timed
    # def convex_delegations(self):
    #     if self.config['convex_delegations']:   
    #         from app.convex.delegations.fetch import fetch 
    #         # from app.convex.locker.process_flipside import process_and_save

    #         return self._helper(fetch, process_and_save)

    ## NEED SNAPSHOT
       
    """
    StakeDAO
    """
    
    # @timed
    # def stakedao_delegations(self):
    #     if self.config['stakedao_delegations']:   
    #         from app.stakedao.delegations.fetch import fetch
    #         # from app.convex.locker.process_flipside import process_and_save

    #         return self._helper(fetch, process_and_save)
      
    @timed
    def stakedao_staked_sdcrv(self):
        if self.config['stakedao_staked_sdcrv']:   
            from app.stakedao.staked_sdcrv.fetch import fetch 
            from app.stakedao.staked_sdcrv.process_flipside import process_and_save

            return self._helper(fetch, process_and_save)   

    @timed
    def stakedao_locker(self):
        if self.config['stakedao_locker']:   
            from app.stakedao.locker.fetch import fetch 
            from app.stakedao.locker.process_flipside import process_and_save

            return self._helper(fetch, process_and_save)   

    @timed
    def stakedao_snapshot_curve(self):
        if self.config['stakedao_snapshot_curve']:   
            from app.stakedao.snapshot.fetch import fetch 
            # from app.convex.locker.process_flipside import process_and_save

            return self._helper(fetch, None)

    @timed
    def stakedao_snapshot_curve_from_snapshot(self):
        if self.config['stakedao_snapshot_curve']:   
            if self.should_fetch:
                space_address = 'sdcrv.eth'
                first = 1000
                skip = 0
                target = None
                snapshot = SnapshotAsSource(space_address, first, skip, target )
                snapshot.save_files('stakedao')

    """
    Votium
    """
    # @timed
    # def votium_bounties(self):
    #     if self.config['votium_bounties_v1']:   
    #         from app.convex.votium_bounties_v2.fetch import fetch 
    #         # from app.convex.locker.process_flipside import process_and_save
    #         return self._helper(fetch, None)
        
    @timed
    def votium_bounties_v2(self):
        if self.config['votium_bounties_v2']:   
            from app.convex.votium_bounties_v2.fetch import fetch 
            from app.convex.votium_bounties_v2.process_flipside import process_and_save

            return self._helper(fetch, process_and_save)


    """
    Warden
    """
    
    # @timed
    # def warden_vesdt_boost_delegation(self):
    #     if self.config['warden_vesdt_boost_delegation']:   
    #         from app.warden.vesdt_boost_delegation.fetch import fetch 
    #         # from app.warden.vesdt_boost_delegation.process_flipside import process_and_save

    #         return self._helper(fetch, process_and_save)  

    """
    Utility
    """
    def _helper(self, fetch, process_and_save, override_load_initial = None):
        if self.should_fetch:
            if fetch != None:
                if override_load_initial == None:
                    fetch(self.load_initial)
                else:
                    fetch(override_load_initial)
        # Always process if config is True
        if process_and_save != None:
            return process_and_save()
        else:
            print(f"Not Processing: {process_and_save}")
        return None

    # def liquidity_helper(self, fetch, process_and_save, override_load_initial = None):
    #     if self.should_fetch:
    #         if fetch != None:
    #             if override_load_initial == None:
    #                 fetch(self.load_initial)
    #             else:
    #                 fetch(override_load_initial)
    #         if process_and_save != None:
    #             return process_and_save()
    #     return None



    