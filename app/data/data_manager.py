from app.utilities.utility import timed, print_mode

from app.data.local_storage import (
    read_json,
    read_csv,
    write_json,
    csv_to_df,
    df_to_csv,
)
# from app.data.local_storage import get_cwd
# import pandas as pd

load_initial = False
should_fetch = True
should_process = False
DEFAULT_BOOL = False

manager_config = {
    # Curve
    'get_all_gauges': DEFAULT_BOOL,
    'gauge_to_lp_map': DEFAULT_BOOL,
    'curve_locker': DEFAULT_BOOL,
    'curve_gauge_votes': DEFAULT_BOOL,
    'curve_gauge_checkpoints': DEFAULT_BOOL,

    'curve_liquidity': DEFAULT_BOOL, ## New Source Now
    'curve_crv_price': DEFAULT_BOOL,
    
    # Convex
    'convex_locker': DEFAULT_BOOL,
    'convex_delegations': DEFAULT_BOOL,
    'convex_snapshot_curve': DEFAULT_BOOL,
    
    # StakeDAO
    'stakedao_delegations': DEFAULT_BOOL,
    'stakedao_staked_sdcrv': DEFAULT_BOOL,
    'stakedao_locker': DEFAULT_BOOL,
    'stakedao_snapshot_curve': DEFAULT_BOOL,

    #Votium
    'votium_bounties_v2': DEFAULT_BOOL,
    # Warden
    'warden_vesdt_boost_delegation': False,

    # Address Book
    'address_book_actors': DEFAULT_BOOL,
}

# run['curve_locker'] = True
# run['stakedao_locker'] = True



class Manager():
    def __init__(self,
                manager_config=manager_config,
                should_fetch=should_fetch,
                should_process =should_process,
                load_initial = load_initial,
                # Curve Liquidity Focus
                load_cutoff = False,   
                cutoff_value = None,
                should_loop_liquidity = False,
                human_management = False,
                ):
        # print(manager_config)
        self.config = manager_config
        self.should_fetch = should_fetch
        self.should_process = should_process
        self.load_initial = load_initial
        self.load_liquidity_cutoff = load_cutoff
        self.liquidity_cutoff_value = cutoff_value
        self.should_loop_liquidity = should_loop_liquidity
        self.human_management = human_management

    def update_settings(self, new_settings):
        self.config = new_settings['manager_config'] if 'manager_config' in new_settings else None
        self.should_fetch = new_settings['should_fetch'] if 'should_fetch' in new_settings else False
        self.should_process = new_settings['should_process'] if 'should_process' in new_settings else False
        self.load_initial = new_settings['load_initial'] if 'load_initial' in new_settings else False
        self.load_liquidity_cutoff = new_settings['load_cutoff'] if 'load_cutoff' in new_settings else False
        self.liquidity_cutoff_value = new_settings['cutoff_value'] if 'cutoff_value' in new_settings else None
        self.should_loop_liquidity = new_settings['should_loop_liquidity'] if 'should_loop_liquidity' in new_settings else False
        self.human_management = new_settings['human_management'] if 'human_management' in new_settings else False

    def manage(self):
        # Curve
        self.get_all_gauges()
        self.gauge_to_lp_map()
        self.curve_locker()
        self.curve_gauge_votes()
        self.curve_gauge_rounds()
        self.curve_liquidity()

        # Convex
        self.convex_locker()
        # self.convex_snapshot_curve_from_snapshot()  # Do First
        self.convex_snapshot_curve()                # Do Second
        self.convex_delegations()
        
        # StakeDAO
        self.stakedao_staked_sdcrv()
        self.stakedao_locker()
        # self.stakedao_snapshot_curve_from_snapshot()    # Do First
        self.stakedao_snapshot_curve()                  # Do Second
        self.stakedao_delegations()

        # Votium
        self.votium_bounties_v2()
        self.votium_bounties_v1()
        # Warden

        # Address Book
        self.address_book_actors()

    """
    Curve
    """
    @timed
    def get_all_gauges(self):
        if 'get_all_gauges' in self.config and self.config['get_all_gauges']:   
            from app.data.reference import filename_get_all_gauges
            import requests
            if self.should_fetch:
                url = 'https://api.curve.fi/api/getAllGauges'
                r = requests.get(url)
                resp = r.json()
                write_json(filename_get_all_gauges, resp['data'], 'source')
            # from app.curve.gauges.process_flipside import process_and_get 

            return 
        
    @timed
    def gauge_to_lp_map(self):
        if 'gauge_to_lp_map' in self.config and self.config['gauge_to_lp_map']:   
            from app.curve.gauges.fetch import fetch 
            from app.curve.gauges.process_flipside import process_and_save 
            # from app.curve.gauges.process_flipside import process_and_get 

            return self._helper(fetch, process_and_save, True)
    
    @timed
    def curve_locker(self):
        if 'curve_locker' in self.config and self.config['curve_locker']:   
            from app.curve.locker.fetch import fetch 
            from app.curve.locker.process_flipside import process_and_save 

            return self._helper(fetch, process_and_save)
    
    @timed
    def curve_gauge_votes(self):
        if 'curve_gauge_votes' in self.config and self.config['curve_gauge_votes']:   
            from app.curve.gauge_votes.fetch import fetch 
            from app.curve.gauge_votes.process_flipside import process_and_save 

            return self._helper(fetch, process_and_save)
    
    @timed
    def curve_gauge_rounds(self):
        if 'curve_gauge_checkpoints' in self.config and self.config['curve_gauge_checkpoints']:   
            from app.curve.gauge_checkpoints.process_flipside import process_and_save 

            return self._helper(None, process_and_save)
        
    @timed
    def curve_liquidity(self):
        if 'curve_liquidity' in self.config and self.config['curve_liquidity']:   
            from app.curve.liquidity.liquidity_data_manager import LiquidityManager
            from app.curve.liquidity.process_flipside import process_and_save 
            liquidity_manager = LiquidityManager(
                self.should_fetch, 
                self.load_initial, 
                self.load_liquidity_cutoff,
                self.liquidity_cutoff_value,
                self.should_loop_liquidity,
                self.human_management)
            liquidity_manager.manage()
            return self._helper(None, process_and_save)
        

    
    """
    Convex
    """
    
    @timed
    def convex_locker(self):
        if 'convex_locker' in self.config and self.config['convex_locker']:   
            from app.convex.locker.fetch import fetch 
            from app.convex.locker.process_flipside import process_and_save

            return self._helper(fetch, process_and_save)

    @timed
    def convex_snapshot_curve(self):
        if 'convex_snapshot_curve' in self.config and self.config['convex_snapshot_curve']:   
            from app.convex.snapshot.fetch import fetch 
            from app.snapshot.votes.process import process_and_save_helper
            from app.data.reference import (
                filename_convex_curve_snapshot, 
                filename_convex_curve_snapshot_origin
                )
            self._helper(fetch, None)
            if self.should_process:
                process_and_save_helper(
                    filename_convex_curve_snapshot, 
                    filename_convex_curve_snapshot_origin
                    )
            return 
        
    # @timed
    # def convex_snapshot_curve_from_snapshot(self):
    #     if 'convex_snapshot_curve' in self.config and self.config['convex_snapshot_curve']: 
    #         from app.snapshot.alt_models import SnapshotAsSource

    #         if self.should_fetch:
    #             space_address = 'cvx.eth'
    #             first = 200
    #             skip = 0
    #             target = None
    #             snapshot = SnapshotAsSource(space_address, first, skip, target )
    #             snapshot.save_files('convex')

            # from app.convex.snapshot.fetch import fetch 
            # from app.convex.locker.process_flipside import process_and_save

            # return self._helper(fetch, None)
    @timed
    def convex_delegations(self):
        if 'convex_delegations' in self.config and self.config['convex_delegations']:   
            from app.convex.delegations.fetch import fetch 
            from app.convex.delegations.process_flipside import process_and_save

            return self._helper(fetch, process_and_save)

       
    """
    StakeDAO
    """
    
    # @timed
    # def stakedao_delegations(self):
    #     if 'stakedao_delegations' in self.config and self.config['stakedao_delegations']:   
    #         from app.stakedao.delegations.fetch import fetch
    #         # from app.convex.locker.process_flipside import process_and_save

    #         return self._helper(fetch, process_and_save)
      
    @timed
    def stakedao_staked_sdcrv(self):
        if 'stakedao_staked_sdcrv' in self.config and self.config['stakedao_staked_sdcrv']:   
            from app.stakedao.staked_sdcrv.fetch import fetch 
            from app.stakedao.staked_sdcrv.process_flipside import process_and_save

            return self._helper(fetch, process_and_save)   

    @timed
    def stakedao_locker(self):
        if 'stakedao_locker' in self.config and self.config['stakedao_locker']:   
            from app.stakedao.locker.fetch import fetch 
            from app.stakedao.locker.process_flipside import process_and_save

            return self._helper(fetch, process_and_save)   

    @timed
    def stakedao_snapshot_curve(self):
        if 'stakedao_snapshot_curve' in self.config and self.config['stakedao_snapshot_curve']:   
            from app.stakedao.snapshot.fetch import fetch 
            from app.snapshot.votes.process import process_and_save_helper
            from app.data.reference import (
                filename_stakedao_curve_snapshot, 
                filename_stakedao_curve_snapshot_origin
                )
            self._helper(fetch, None)
            if self.should_process:
                process_and_save_helper(
                    filename_stakedao_curve_snapshot, 
                    filename_stakedao_curve_snapshot_origin
                    )
    # @timed
    # def stakedao_snapshot_curve_from_snapshot(self):
    #     if 'stakedao_snapshot_curve' in self.config and self.config['stakedao_snapshot_curve']:  
    #         from app.snapshot.alt_models import SnapshotAsSource
 
    #         if self.should_fetch:
    #             space_address = 'sdcrv.eth'
    #             first = 1000
    #             skip = 0
    #             target = None
    #             snapshot = SnapshotAsSource(space_address, first, skip, target )
    #             snapshot.save_files('stakedao')

    @timed
    def stakedao_delegations(self):
        if 'stakedao_delegations' in self.config and self.config['stakedao_delegations']:   
            from app.stakedao.delegations.fetch import fetch 
            from app.stakedao.delegations.process_flipside import process_and_save

            return self._helper(fetch, process_and_save)

    """
    Votium
    """
    @timed
    def votium_bounties_v1(self):
        if 'votium_bounties_v1' in self.config and self.config['votium_bounties_v1']:   
            from app.convex.votium_bounties.fetch import fetch 
            # from app.convex.locker.process_flipside import process_and_save
            return self._helper(fetch, None)
        
    @timed
    def votium_bounties_v2(self):
        if 'votium_bounties_v2' in self.config and self.config['votium_bounties_v2']:   
            from app.convex.votium_bounties_v2.fetch import fetch 
            from app.convex.votium_bounties_v2.process_flipside import process_and_save

            return self._helper(fetch, process_and_save)


    """
    Warden
    """
    
    # @timed
    # def warden_vesdt_boost_delegation(self):
    #     if 'warden_vesdt_boost_delegation' in self.config and self.config['warden_vesdt_boost_delegation']:   
    #         from app.warden.vesdt_boost_delegation.fetch import fetch 
    #         # from app.warden.vesdt_boost_delegation.process_flipside import process_and_save

    #         return self._helper(fetch, process_and_save)  

    """
    Address Book
    """
    def address_book_actors(self):
        if 'address_book_actors' in self.config and self.config['address_book_actors']:
            from app.address_book.actors.process_models import process_and_save

            return self._helper(None, process_and_save)



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

        if process_and_save != None:
            if self.should_process:
                return process_and_save()
        print_mode(f"Not Processing: {process_and_save}")
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



    