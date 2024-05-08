from flask import current_app as app

from app.data.local_storage import (
    pd,
    csv_to_df,
    )

from app.utilities.utility import nullify_list

from app.data.reference import (
    known_large_market_actors,
)

from .models import format_df

class ProcessSnapshotDelegations():
    def __init__(self, df_delegations, df_snapshot_votes, df_locker, is_not_convex = False):
        # Existing
        self.df_delegations = format_df(df_delegations)
        self.df_snapshot_votes = df_snapshot_votes
        self.df_locker = df_locker
        # New
        self.delegator_per_proposal = []    # aggregates delegator per proposal
        self.delegator_locks_per_proposal = [] # delegator per proposal plus lock info
        # self.aggregate_delegates = []  # sum balance per delegate per epoch and proposal
        # self.locks_with_delegate_context = [] # df_aggregate_user_epoch + delegate identifier per epoch
        # self.votes_with_delegate_context = []

        self.is_not_convex = is_not_convex
        # self.vote_power = []
        self.process()
        # self.process_aggregate_system()
        # self.process_aggregate_votes()


    
    def process(self):
        # proposal_starts = self.df_snapshot_votes.proposal_start.unique()
        df_proposal_aggs = self.get_snapshot_proposal_aggregates()

        delegator_list = []
        delegator_lock_list = []
        # lock_delegate_list = []
        # vote_deletage_list = []
        df_locker_agg_user_epoch = self.df_locker
        id_list = list(self.df_delegations.id.unique())
        id_list.sort()
        for i, row in df_proposal_aggs.iterrows():
            # delegation

            local_delegators = self.df_delegations[self.df_delegations['block_timestamp'] < row['proposal_start'] ]
            local_delegators = local_delegators.sort_values(['block_timestamp', 'event_name'], ascending=[True, False]).groupby(['delegator', 'id']).tail(1)
            local_delegators['proposal_start'] = row['proposal_start']
            local_delegators['proposal_title'] = row['proposal_title']
            local_delegators['delegator_known_as'] = local_delegators['delegator'].apply(lambda x: self.process_known_as(x) )
            local_delegators['delegate_known_as'] = local_delegators['delegate'].apply(lambda x: self.process_known_as(x) )

            local_delegators = self.prioritize_local_delegation(local_delegators, id_list)
            local_delegators_copy = local_delegators.copy()

            # locks
            if not self.is_not_convex:
                df_lock_local = df_locker_agg_user_epoch[df_locker_agg_user_epoch['this_epoch'] < row['proposal_start'] ]
                target_epoch = df_lock_local.this_epoch.max()
                df_lock_local = df_lock_local[df_lock_local['this_epoch'] == target_epoch ]
                balance_user = 'user'
                balance_var = 'current_locked'
            else:
                df_lock_local = df_locker_agg_user_epoch[df_locker_agg_user_epoch['block_timestamp'] < row['proposal_start'] ]
                df_lock_local = df_lock_local.sort_values(['block_timestamp', 'event_name', 'staked_balance']).groupby(['provider']).tail(1)
                balance_user = 'provider'
                balance_var = 'staked_balance'


            # Join Delegators and Locks
            local_delegators_with_locks = local_delegators_copy[[
                'delegate',
                'delegator',
                'delegate_known_as',
                'delegator_known_as',
                'proposal_start',
                'proposal_title'
                ]].set_index('delegator').join(df_lock_local.set_index(balance_user)).reset_index()
            
            delegator_list.append(local_delegators)
            delegator_lock_list.append(local_delegators_with_locks)

            # Join Locks and Delegates (to reference delegation on locks per epoch per user)
            # df_local_3
            # local_locks_with_delegators = df_lock_local.set_index(balance_user).join(
            #     local_delegators[[
            #         'delegate', 
            #         'delegator',
            #         'delegate_known_as',
            #         'delegator_known_as',
            #         ]].set_index('delegator')
            #     ).reset_index()
            # delegator_lock_list.append(df_local_3)        
            # lock_delegate_list.append(local_locks_with_delegators)

            
        self.delegator_per_proposal = pd.concat(delegator_list)
        df_temp = pd.concat(delegator_lock_list)
        self.delegator_locks_per_proposal = df_temp[df_temp[balance_var] > 0]
        # self.locks_with_delegate_context = pd.concat(lock_delegate_list)
        # self.votes_with_delegate_context = pd.concat(vote_deletage_list)
        return
    
    def process_known_as(self, address):
        if address in known_large_market_actors:
            return known_large_market_actors[address]
        return '_'


    def get_snapshot_proposal_aggregates(self):
        return self.df_snapshot_votes.groupby([
            'proposal_start', 'proposal_title', 'checkpoint_id'
        ]).agg(
        total_choice_power=pd.NamedAgg(column='choice_power', aggfunc=sum),
        voters_count=pd.NamedAgg(column='voter', aggfunc=lambda x: len(x.unique())),
        ).reset_index()

    def prioritize_local_delegation(self, local_delegators, id_list=None):
        # Global delegation is secondary to local delegation
        # If both are present, use local
        if not id_list:
            id_list = list(self.df_delegations.id.unique())

        # Get All delegators with a last record of SetDelegate
        filtered_delegators_set = set(list(local_delegators[(local_delegators['id'] == id_list[-1]) & 
                                            (local_delegators['event_name'] == 'SetDelegate')].delegator.unique()))
        
        filtered_delegators_global = set(list(local_delegators[(local_delegators['id'] == id_list[0]) & 
                                            (local_delegators['event_name'] == 'SetDelegate')].delegator.unique()))
        # Get all local delegators with last record of ClearDelegate
        filtered_delegators_clear = set(list(local_delegators[(local_delegators['id'] == id_list[-1]) & 
                                            (local_delegators['event_name'] == 'ClearDelegate')].delegator.unique()))
        # This list should prioritize local
        filtered_set = filtered_delegators_set.intersection(filtered_delegators_global)
        # This list should default back to global 
        filtered_clear = filtered_delegators_clear.intersection(filtered_delegators_global)

        # If global anything with global id in fitlered_set should be removed
        local_delegators_2 = local_delegators[~(
            (local_delegators['id'] == id_list[0]) &
            local_delegators['delegator'].isin(
                list(filtered_set)
                )
            
            )]
        # If local, anything with local id in filtered_clear should be removed 
        local_delegators_2 = local_delegators_2[~(
            (local_delegators_2['id'] == id_list[-1]) &
            local_delegators_2['delegator'].isin(
                list(filtered_clear)
                )
            
            )]
        return local_delegators_2.copy()