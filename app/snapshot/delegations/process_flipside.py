from flask import current_app as app

from app.data.local_storage import (
    pd,
    csv_to_df,
    )

from app.utilities.utility import nullify_list

from app.data.reference import (
    known_large_market_actors,
)

class ProcessConvexDelegations():
    def __init__(self, df_delegations, df_snapshot_votes, convex_locker ):
        # Existing
        self.df_delegations = df_delegations
        self.df_snapshot_votes = df_snapshot_votes
        self.convex_locker = convex_locker
        # New
        self.delegator_per_proposal = []    # aggregates delegator per proposal
        self.delegator_locks_per_proposal = [] # delegator per proposal plus lock info
        self.aggregate_delegates = []  # sum balance per delegate per epoch and proposal
        self.locks_with_delegate_context = [] # df_aggregate_user_epoch + delegate identifier per epoch

        self.votes_with_delegate_context = []
        # self.vote_power = []
        self.process()
        self.process_aggregate_system()
        self.process_aggregate_votes()


    
    def process(self):
        # proposal_starts = self.df_snapshot_votes.proposal_start.unique()
        df_proposal_aggs = self.get_snapshot_proposal_aggregates()

        delegator_list = []
        delegator_lock_list = []
        lock_delegate_list = []
        vote_deletage_list = []
        pcl_agg_user = self.convex_locker
        
        for i, row in df_proposal_aggs.iterrows():
            # delegation
            local_delegators = self.df_delegations[self.df_delegations['block_timestamp'] < row['proposal_start'] ]
            local_delegators = local_delegators.sort_values(['block_timestamp', 'event_name']).groupby(['delegator']).tail(1)
            local_delegators['proposal_start'] = row['proposal_start']
            local_delegators['proposal_title'] = row['proposal_title']
            local_delegators['delegator_known_as'] = local_delegators['delegator'].apply(lambda x: self.process_known_as(x) )
            local_delegators['delegate_known_as'] = local_delegators['delegate'].apply(lambda x: self.process_known_as(x) )

            local_delegators_copy = local_delegators.copy()

            # locks
            df_lock_local = pcl_agg_user[pcl_agg_user['this_epoch'] < row['proposal_start'] ]
            target_epoch = df_lock_local.this_epoch.max()
            df_lock_local = df_lock_local[df_lock_local['this_epoch'] == target_epoch ]

            # Join Delegators and Locks
            local_delegators_with_locks = local_delegators_copy[[
                'delegate',
                'delegator',
                'delegate_known_as',
                'delegator_known_as',
                'proposal_start',
                'proposal_title'
                ]].set_index('delegator').join(df_lock_local.set_index('user')).reset_index()
            
            delegator_list.append(local_delegators)
            delegator_lock_list.append(local_delegators_with_locks)

            # Join Locks and Delegates (to reference delegation on locks per epoch per user)
            # df_local_3
            local_locks_with_delegators = df_lock_local.set_index('user').join(
                local_delegators[[
                    'delegate', 
                    'delegator',
                    'delegate_known_as',
                    'delegator_known_as',
                    ]].set_index('delegator')
                ).reset_index()
            # delegator_lock_list.append(df_local_3)        
            lock_delegate_list.append(local_locks_with_delegators)

            
        self.delegator_per_proposal = pd.concat(delegator_list)
        temp = pd.concat(delegator_lock_list)
        self.delegator_locks_per_proposal = temp[temp['current_locked'] > 0]
        self.locks_with_delegate_context = pd.concat(lock_delegate_list)
        # self.votes_with_delegate_context = pd.concat(vote_deletage_list)
        return
    
    def process_known_as(self, address):
        if address in known_large_market_actors:
            return known_large_market_actors[address]
        return '_'

    def process_aggregate_system(self):
        df = self.delegator_locks_per_proposal.groupby([
                'proposal_start',
                'proposal_title',
                'delegate_known_as',
                'delegate',
                'this_epoch'
            ]).agg(
            total_delegated=pd.NamedAgg(column='current_locked', aggfunc=sum),
            delegated_lock_count=pd.NamedAgg(column='lock_count', aggfunc=sum),
            delegators_count=pd.NamedAgg(column='delegator', aggfunc=lambda x: len(x.unique())),
            delegators=pd.NamedAgg(column='delegator', aggfunc=list),
            known_delegators=pd.NamedAgg(column='delegator_known_as', aggfunc=list),


        ).reset_index()
        df['delegators'] = df['delegators'].apply(lambda x: nullify_list(x))
        df['known_delegators'] = df['known_delegators'].apply(lambda x: nullify_list(x, True))
        self.aggregate_delegates = df
        return
    
    def get_snapshot_proposal_aggregates(self):
        return self.df_snapshot_votes.groupby([
            'proposal_start', 'proposal_title', 'checkpoint_id'
        ]).agg(
        total_choice_power=pd.NamedAgg(column='choice_power', aggfunc=sum),
        voters_count=pd.NamedAgg(column='voter', aggfunc=lambda x: len(x.unique())),
        ).reset_index()

   
    def process_aggregate_votes(self):
        # self.aggregate_delegates
        # self.df_snapshot_votes
        df = pd.merge(
            self.df_snapshot_votes,
            self.aggregate_delegates,
            how='left',
            left_on=['proposal_title', 'proposal_start', 'voter'],
            right_on=['proposal_title', 'proposal_start', 'delegate' ]
        ).reset_index()
        df['delegators'] = df['delegators'].apply(lambda x: nullify_list(x))
        df['known_delegators'] = df['known_delegators'].apply(lambda x: nullify_list(x, True))
        self.votes_with_delegate_context = df
        return
    

