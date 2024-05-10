from app.convex.locker.models import get_convex_locker_agg_user_epoch
from app.utilities.utility import get_now, pd


# Get Next Unlocks Table
class ConvexUnlocks():
    def __init__(self, df_convex_locker_user_epoch, now=None):
        self.df_convex_locker_user_epoch = df_convex_locker_user_epoch
        self.df_convex_locker_agg_user_epoch = get_convex_locker_agg_user_epoch(df_convex_locker_user_epoch)
        self.now = get_now() if not now else now
        self.df_unlocks = self.process_unlocks()

    def process_unlocks(self):
        df = self.filter_aggs()
        df = self.apply_shifts(df)
        return self.merge_unlocks(df)

    def filter_aggs(self):
        df_local = self.df_convex_locker_agg_user_epoch[
            self.df_convex_locker_agg_user_epoch['this_epoch'] <= self.now
            ]
        l_temp = list(df_local.this_epoch.unique())
        l_temp.sort()
        l_temp[-15]
        return df_local[df_local['this_epoch'] >= l_temp[-17]]

    def apply_shifts(self, df):
        df = df.sort_values('this_epoch')
        # Compare to past records
        df['vs_16'] = (df['current_locked'] / 
            df.groupby(['user', 'known_as', 'display_name'])['current_locked'].shift(16) - 1) * 100
        df['vs_12'] = (df['current_locked'] / 
            df.groupby(['user', 'known_as', 'display_name'])['current_locked'].shift(12) - 1) * 100
        df['vs_08'] = (df['current_locked'] / 
            df.groupby(['user', 'known_as', 'display_name'])['current_locked'].shift(8) - 1) * 100
        df['vs_04'] = (df['current_locked'] / 
            df.groupby(['user', 'known_as', 'display_name'])['current_locked'].shift(4) - 1) * 100
        df['vs_02'] = (df['current_locked'] / 
            df.groupby(['user', 'known_as', 'display_name'])['current_locked'].shift(2) - 1) * 100
        # Cut down to single record per user
        return df[df['this_epoch'] == df.this_epoch.max()]
    
    def merge_unlocks(self, df):
        df_next_unlock = self.get_unlocks(df.this_epoch.max())
        return pd.merge(
                df,
                df_next_unlock,
                how='left',
                left_on=['user'],
                right_on=['user']
            ).reset_index()

    def get_unlocks(self, target_epoch):
        df_next_unlock = self.df_convex_locker_user_epoch[self.df_convex_locker_user_epoch['this_epoch'] == target_epoch]
        df_next_unlock = df_next_unlock[df_next_unlock['epoch_end'] == df_next_unlock.epoch_end.min()]
        return df_next_unlock[
            ['user', 'current_locked', 'epoch_end']
            ].rename(columns={'current_locked':'next_unlock'})
        
    