# from app.data.reference import filename_convex_curve_snapshot, filename_convex_curve_snapshot_origin

from flask import current_app as app
from app import MODELS_FOLDER_PATH, RAW_FOLDER_PATH

from app.data.local_storage import (
    pd,
    csv_to_df,
    df_to_csv,
    )

# filename = 'crv_locker_logs'

from app.snapshot.votes.process_flipside import Snapshot
from app.snapshot.votes.process_snapshot import merge_target
from app.utilities.utility import print_mode
 
print_mode("Loading... { convex.snapshot.models }")


# def get_df_snapshot(filename):
#     filename =  # + current_file_title
#     try:
#         df_snapshot = csv_to_df(filename, RAW_FOLDER_PATH)
#         df_snapshot = df_snapshot[~df_snapshot['proposal_title'].str.contains('FXN')]
#         return df_snapshot.sort_values("vote_timestamp", axis = 0, ascending = True)
#     except:
#         snapshot_dict = read_json(filename, RAW_FOLDER_PATH)
#         df_snapshot = pd.json_normalize(snapshot_dict)
#         df_snapshot = df_snapshot[~df_snapshot['PROPOSAL_TITLE'].str.contains('FXN')]
#         return df_snapshot.sort_values("VOTE_TIMESTAMP", axis = 0, ascending = True)
    

# def get_snapshot_obj(df_snapshot):
#     snapshot = Snapshot()
#     snapshot.process(df_snapshot)
#     return snapshot

# def get_df_vote_choice(snapshot):
#     """
#     THIS RIGHT HERE NEEDS TO BE LOOKED AT
#     """
#     vote_choice_data = snapshot.format_final_choice_output()
#     df_vote_choice = pd.json_normalize(vote_choice_data)
#     return df_vote_choice.sort_values("proposal_start", axis = 0, ascending = True)


# def get_aggregates(df_vote_choice):
#     df_vote_aggregates = df_vote_choice.groupby(
#         ['checkpoint_id', 'checkpoint_timestamp','proposal_start', 'proposal_end', 'proposal_title', 'choice', 'choice_index', 'gauge_addr']
#         )['choice_power'].agg(['sum','count']).reset_index()

#     df_vote_aggregates = df_vote_aggregates.rename(columns={
#         "sum": 'total_vote_power',
#         'count': 'cvx_voter_count'})
#     df_vote_aggregates =df_vote_aggregates.sort_values(["proposal_end", 'total_vote_power', 'gauge_addr'], axis = 0, ascending = False)

#     return df_vote_aggregates


"""
Snapshot has worse rate limiting
But sometimes Flipside is rate limited
So does bulk of pulls from flipside, but gets latest from Snapshot
"""

class MetaSnapshotProcess():
    def __init__(self, filename_flipside, filename_snapshot):
        self.filename_flip = filename_flipside
        self.filename_snap = filename_snapshot
        self.proposal_choice_map = None
        self.df_vote_choice = self.process()
        self.save()
        # self.proposal_choice_map = {}   

    def get_df_snapshot_from_flipside(self):
        df_snapshot_flip_raw = csv_to_df(self.filename_flip, RAW_FOLDER_PATH)
        df_snapshot_flip_raw = df_snapshot_flip_raw[~df_snapshot_flip_raw['proposal_title'].str.contains('FXN')]
        return df_snapshot_flip_raw.sort_values("vote_timestamp", axis = 0, ascending = True)
    
    def get_df_snap_vote_choice(self):
        try:
            temp = csv_to_df(self.filename_snap, RAW_FOLDER_PATH)
            temp = self.format(temp)
            return temp
        except:
            return []

    def get_flipside_obj(self):
        snapshot = Snapshot()
        snapshot.process(self.get_df_snapshot_from_flipside())
        return snapshot
    
    def get_df_flip_vote_choice(self):
        flip_snap_obj = self.get_flipside_obj()
        vote_choice_data = flip_snap_obj.format_final_choice_output()
        df_vote_choice = pd.json_normalize(vote_choice_data)
        self.proposal_choice_map = flip_snap_obj.format_choice_map_output()
        return df_vote_choice.sort_values("proposal_start", axis = 0, ascending = True)

    def format(self, df):
        df['choice_index'] = df['choice_index'].astype(int)
        df['voting_weight'] = df['voting_weight'].astype(float)
        df['total_weight'] = df['total_weight'].astype(float)
        df['choice_percent'] = df['choice_percent'].astype(float)
        df['available_power'] = df['available_power'].astype(float)
        df['choice_power'] = df['choice_power'].astype(float)
        df['valid'] = df['valid'].astype(bool)
        df['checkpoint_timestamp'] = pd.to_datetime(df['checkpoint_timestamp'])
        df['checkpoint_id'] = df['checkpoint_id'].astype(int)

        return df 

    def process(self):
        df_flip = self.get_df_flip_vote_choice()
        df_snap = self.get_df_snap_vote_choice()
        df_merge = self.merge_vote_choice(df_flip, df_snap)
        return self.reduce_duplicate_votes(df_merge)
    
    def reduce_duplicate_votes(self, df):
        df_temp = df.groupby(['checkpoint_id'])['proposal_end'].max().reset_index(name='max_end')
        df_combo = pd.merge(
            df, 
            df_temp, 
            how='left', 
            on = ['checkpoint_id' ], 
            )
        df = df_combo[df_combo['proposal_end'] == df_combo['max_end']]
        df = df.drop(columns=['max_end'])
        return df

    def get_flipside_vote_choice(self, snapshot):
        vote_choice_data = snapshot.format_final_choice_output()
        df_vote_choice = pd.json_normalize(vote_choice_data)
        return df_vote_choice.sort_values("proposal_start", axis = 0, ascending = True)


        
    def merge_vote_choice(self, df_flip, df_snap):
        # if no data return untouched
        if not len(df_snap) > 0:
            return df_flip
        # clear out overlap
        for title in df_snap.proposal_title.unique():
            # print(f"Removing: {title}")
            df_flip = df_flip[~df_flip['proposal_title'].str.match(title)]
        # merge the things
        df_vote_choice = pd.concat([df_flip, df_snap])
        
        return df_vote_choice


    def save(self):
        df_to_csv(self.df_vote_choice, self.filename_flip, MODELS_FOLDER_PATH)


def process_and_save_helper(flip_file, snap_file):
    msp = MetaSnapshotProcess(flip_file, snap_file)
    
