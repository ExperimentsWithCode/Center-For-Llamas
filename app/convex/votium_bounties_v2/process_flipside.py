from flask import current_app as app
from app.data.reference import filename_votium_v2

from datetime import datetime, timedelta
from app.utilities.utility import (
    timed,
    get_datetime_obj,
    get_checkpoint_id,
    get_checkpoint_timestamp_from_date,
    nullify_amount
)
from app.data.local_storage import (
    pd,
    read_json, 
    read_csv,  
    write_dataframe_csv,
    write_dfs_to_xlsx
    )

try:
    df_checkpoints_agg = app.config['df_checkpoints_agg']
    # df_curve_liquidity_aggregates = app.config['df_curve_liquidity_aggregates']
    # df_curve_liquidity = app.config['df_curve_liquidity']
    # df_convex_snapshot_vote_aggregates = app.config['df_convex_snapshot_vote_aggregates']

except:
    from app.curve.gauge_rounds.models import df_checkpoints_agg
    # from app.curve.liquidity.models import df_curve_liquidity_aggregates, df_curve_liquidity
    # from app.convex.snapshot.models import df_convex_snapshot_vote_aggregates

class ProcessVotiumV2():
    def __init__(self, df_votium):
        self.df_votium = self.get_df_votium()
        self.bounty_checkpoint_map = self.associate_rounds_with_checkpoints()

    def get_df_votium(self):
        filename = filename_votium_v2    #+ fallback_file_title
        resp_dict = read_csv(filename, 'raw_data')
        df = pd.json_normalize(resp_dict)
        df = self.format(df)
        df = df.sort_values("block_timestamp", axis = 0, ascending = True)
        return df   
    
    def format(self, df):
        df['bounty_amount'] = df.apply(
            lambda x: nullify_amount(x['bounty_amount']), 
            axis=1)
        df['bounty_value'] = df.apply(
            lambda x: nullify_amount(x['bounty_value']), 
            axis=1)
        # df['votium_round'] = df.apply(
        #     lambda x: nullify_amount(x['votium_round']), 
        #     axis=1)
        df = df[df['votium_round'] != ''].copy()

        df['votium_round'] = df['votium_round'].astype(int)

        return df
    
    # def process(self):
    #     return self.foo()


    def associate_rounds_with_checkpoints(self):
        start_time = get_datetime_obj('2023-09-01 19:29:59.000')

        this_period = get_checkpoint_id(start_time)

        current_round = 52
        end_round = int(self.df_votium['votium_round'].max())
        bounty_checkpoint_map = {}
        bounty_checkpoint_map[current_round] = 52
        while current_round <= end_round:
            this_period += 2
            bounty_checkpoint_map[current_round] = this_period
            current_round += 1
        bounty_checkpoint_map[None] = ''
        return bounty_checkpoint_map


    def process(self):
        votium_v2 = self.df_votium.copy()
        bounty_checkpoint_map = self.bounty_checkpoint_map.copy()
        # Find checkpoint
        votium_v2["checkpoint_id"] = votium_v2['votium_round'].apply(lambda x : bounty_checkpoint_map[x])
        # Filter for merge
        votium_v2_temp = votium_v2[[
            'block_timestamp',
            'checkpoint_id',
            'gauge_addr',
            'bounty_amount',
            'bounty_value',
            'token_name',
            'token_symbol',
            'votium_round',
            ]]
        # convex_snapshot_temp = df_convex_snapshot_vote_aggregates[['checkpoint_id', 'checkpoint_timestamp', 'choice', 'gauge_addr', 'total_vote_power']]
        curve_vote_temp = df_checkpoints_agg[[
            'checkpoint_id',
            'checkpoint_timestamp',
            'gauge_addr',
            'gauge_name',
            'gauge_symbol',
            'total_vote_power',
            'total_vote_percent',
            ]]
        # Merge
        ## Merge Convex
        # df_combo = pd.merge(convex_snapshot_temp, votium_v2, how='left', left_on = ['gauge_addr', 'checkpoint_id'], right_on = ['gauge_addr', 'checkpoint_id'])

        df_combo = pd.merge(votium_v2, curve_vote_temp, how='inner', left_on = ['gauge_addr', 'checkpoint_id'], right_on = ['gauge_addr', 'checkpoint_id'])
        
        # try:
        df_sums = df_combo.groupby([
            'checkpoint_id',
            'gauge_addr',
            'votium_round',
            ]).agg(
                total_bounty_value=pd.NamedAgg(column='bounty_value', aggfunc=sum)
                ).reset_index()
        df_combo = pd.merge(
            df_combo,
            df_sums,
            how='left',
            left_on=['checkpoint_id', 'gauge_addr', 'votium_round'],
            right_on=['checkpoint_id', 'gauge_addr', 'votium_round']
        )

        df_combo['relative_vote_power'] = df_combo['total_vote_power'] * (df_combo['bounty_value'] / df_combo['total_bounty_value'])
        df_combo['bounty_per_vecrv'] = df_combo['total_bounty_value'] / df_combo['total_vote_power']
        df_combo['bounty_per_vecrv_percent'] = df_combo['total_bounty_value'] / df_combo['total_vote_percent']
        df_combo['vecrv_per_bounty'] = df_combo['total_vote_power'] / df_combo['total_bounty_value']
        df_combo['vecrv_percent_per_bounty'] = df_combo['total_vote_percent'] / df_combo['total_bounty_value']
        df_combo = df_combo.sort_values(['votium_round', 'total_bounty_value'], ascending=False)
        print(f"Votium Length: {len(votium_v2_temp)}")
        print(f"Total Output Length: {len(df_combo)}")
        return df_combo
    

def get_df_votium():
    filename = filename_votium_v2    #+ fallback_file_title
    resp_dict = read_csv(filename, 'raw_data')
    df = pd.json_normalize(resp_dict)
    df = df.sort_values("block_timestamp", axis = 0, ascending = True)
    return df   



def process_and_save():
    print("Processing... { curve.liquidity.models }")
    votium_v2 = ProcessVotiumV2(get_df_votium())
    df_votium_v2 = votium_v2.process()   

    write_dataframe_csv(filename_votium_v2, df_votium_v2, 'processed')

    try:
        # app.config['df_active_votes'] = df_active_votes
        app.config['df_votium_v2'] = df_votium_v2
    except:
        print("could not register in app.config\n\tVotium v2")
    return {
        # 'df_active_votes': df_active_votes,
        'df_votium_v2': df_votium_v2,
    }