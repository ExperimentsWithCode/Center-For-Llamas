import traceback

from flask import current_app as app

from app.data.local_storage import (
    pd,
    read_json,
    read_csv,
    write_dataframe_csv,
    write_dfs_to_xlsx
    )

# filename = 'crv_locker_logs'

from datetime import datetime as dt

from app.utilities.utility import get_period, get_period_end_date, get_period_direct, get_convex_period_direct
from app.data.reference import (
    known_large_curve_holders,
    current_file_title,
    fallback_file_title
)

from app.data.source.harvested_core_pools import core_pools



gauge_registry = app.config['gauge_registry']
proposal_choice_map = app.config['proposal_choice_map']
df_vote_aggregates = app.config['df_vote_aggregates'] 



class VBRegistry():
    def __init__(self):
        self.bounty_list = []

    def process_bounties(self, df):
        for i, row in df.iterrows():
            try:
                b = Bounty(row)
                self.bounty_list.append(b)
            except Exception as e:
                # pass
                print(e)
                print(row)
                print(traceback.format_exc())


    
    def format_output(self):
        output_data = []
        for b in self.bounty_list:
            output_data.append(b.format_output())
        return output_data

class Bounty():
    def __init__(self, row):
        # self.timestamp = row['block_timestamp']
        if 'block_timestamp' in row:
            try:
                split = row['block_timestamp'].split("T")
                row['block_timestamp'] = split[0]+" "+split[1][:-1]
            except:
                pass
        self.block_timestamp = row['block_timestamp']
        self.choice_index = int(row['choice_index'])
        self.token_symbol = row['token_symbol']
        self.amount = float(row['amount'])
        self.bounty_value = float(row['bounty_value']) if not row['bounty_value'] == "" else 0
        # self.amount_adj = self.amount / 10**18
        self.bounty_token_address = row['bounty_token_address']
        self.origin_from_address = row['origin_from_address']
        self.period = get_convex_period_direct(row['block_timestamp'])
        self.period_end_date = None # get_period_end_date(row['block_timestamp'])

        self.gauge_ref = self.get_gauge_ref()
        self.gauge_address = self.get_gauge_address()
        self.total_vote_power = 0
        self.voter_count = 0
        self.get_meta()
        if self.bounty_value > 100 and self.total_vote_power >100:
            self.votes_per_dollar = self.total_vote_power / self.bounty_value 
            self.price_per_vote = self.bounty_value / self.total_vote_power
        else:
            self.votes_per_dollar = 0
            self.price_per_vote = 0


    def get_gauge_ref(self):
        if self.period in proposal_choice_map:
            if self.choice_index < len(proposal_choice_map[self.period]):
                return proposal_choice_map[self.period][self.choice_index]
            else:
                print("_"*50)
                print (self.period)
                print (len(proposal_choice_map[self.period]))
                return "Not Found"
        
    def get_gauge_address(self):
        return gauge_registry.get_gauge_address_from_snapshot(self.gauge_ref)

    def get_meta(self):
        try:
            df_aggs = df_vote_aggregates[(df_vote_aggregates['period']== self.period) & 
                                    (df_vote_aggregates['choice']== self.gauge_ref)]
            self.total_vote_power = df_aggs.iloc[0]['total_vote_power']
            self.voter_count = df_aggs.iloc[0]['vlcvx_voter_count']
            # self.period = df_aggs.iloc[0]['period']
            self.period_end_date = df_aggs.iloc[0]['period_end_date']
        except Exception as e:
            print(self.period)
            print(self.gauge_ref)
            print(df_vote_aggregates.choice)
            print(e)
            print(traceback.format_exc())


    def format_output(self):
        return {
            'block_timestamp': self.block_timestamp,
            'gauge_ref': self.gauge_ref,
            'gauge_addr': self.gauge_address,
            'period': self.period,
            'period_end_date': self.period_end_date,
            'token_address': self.bounty_token_address,
            'token_symbol': self.token_symbol,
            'amount': self.amount,
            'bounty_value': self.bounty_value,
            'price_per_vote': self.price_per_vote,
            'votes_per_dollar': self.votes_per_dollar,
            'total_vote_power': self.total_vote_power,
            'total_vote_count': self.voter_count,
        }
    # def fill_in(self, proposals):
    #     proposals.search
    #     proposals = df_vote_aggregates[df_vote_aggregates['proposal_end'] == current_period]
        


def get_df_bounty_for_round():
    filename = 'votium_bounty_for_round' #+ current_file_title
    resp_dict = read_csv(filename, 'source')
    df_stakedao_events_created = pd.json_normalize(resp_dict)
    return df_stakedao_events_created.sort_values("block_timestamp", axis = 0, ascending = True)

def get_df_bounty_formatted(df):
    vbr = VBRegistry()
    vbr.process_bounties(df)
    temp = vbr.format_output()
    # print(temp)
    df_bounty_formatted = pd.json_normalize(temp)
    return df_bounty_formatted.sort_values("block_timestamp", axis = 0, ascending = False)


df_bounty_for_round = get_df_bounty_for_round()

df_bounty_formatted = get_df_bounty_formatted(df_bounty_for_round)

# print(df_bounty_formatted.head())