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


try:
    from flask import current_app as app

    gauge_registry = app.config['gauge_registry']
    convex_snapshot_proposal_choice_map = app.config['convex_snapshot_proposal_choice_map']
    df_vote_aggregates = app.config['df_convex_snapshot_vote_aggregates'] 
except: 
    from app.curve.gauges.models import gauge_registry
    from app.convex.snapshot.models import convex_snapshot_proposal_choice_map
    from app.convex.snapshot.models import df_convex_snapshot_vote_aggregates as df_vote_aggregates

print("Loading... { convex.votium_bounties.models }")

class VBRegistry():
    def __init__(self):
        self.bounty_list = []
        self.bounty_map = {}
        # self.ref_index_map = {}

    def process_bounties(self, df):
        # Load Bounties
        for i, row in df.iterrows():
            try:
                b = Bounty(row)
                self.bounty_list.append(b)
            except Exception as e:
                pass
                # print(e)
                # print(row)
                # print(traceback.format_exc())
            if not b.period in self.bounty_map:
                self.bounty_map[b.period] = {}
            # Group Bounties
            if not b.choice_index in self.bounty_map[b.period]:
                self.bounty_map[b.period][b.choice_index] = []
            self.bounty_map[b.period][b.choice_index].append(b)
        # Process relative bounty influence on vote weight
        for period in self.bounty_map:
            for choice_index in self.bounty_map[period]:
                like_bounty_list = self.bounty_map[period][int(choice_index)]
                total_bounty_value = 0
                for bounty in like_bounty_list:
                    total_bounty_value += bounty.bounty_value

                if total_bounty_value > 0:
                    for bounty in like_bounty_list:
                            relative_bounty_weight = bounty.bounty_value / total_bounty_value
                            bounty.update_derrived_stats(relative_bounty_weight)

    def get_bounty_paid(self, period, choice_index, vote_power):
        try:
            bounties = self.bounty_map[period][int(choice_index)]
            bounty_paid = 0
            for bounty in bounties:
                bounty_paid += (vote_power / bounty.relative_vote_power) * bounty.bounty_value
            # print(f"bounty {bounty_paid}")
            return bounty_paid
        except Exception as e:
            # print("_"*50)
            # print(e)
            # print(traceback.format_exc())
            # print(f"period {period}, type: {type(period)}")
            # print(f"period {choice_index}, type: {type(choice_index)}")
            return 0
    
    def get_bounty_currency(self, period, choice_index):
        try:
            bounties = self.bounty_map[period][int(choice_index)]
            bounty_symbols = []
            for bounty in bounties:
                bounty_symbols.append(bounty.token_symbol)

            return ', '.join(bounty_symbols)
        except:
            return None
    
    def get_bounty_aggregate(self, period, choice_index):
        try:
            bounties = self.bounty_map[period][int(choice_index)]
            total_value = 0
            for bounty in bounties:
                total_value += bounty.bounty_value
            return total_value
        except Exception as e:
            # print("_"*50)
            # print(e)
            # print(traceback.format_exc())
            # print(f"period {period}, type: {type(period)}")
            # print(f"period {choice_index}, type: {type(choice_index)}")
            return 0
        
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
        self.period_end_date = get_period_end_date(row['block_timestamp'])

        self.gauge_ref = self.get_gauge_ref()
        self.gauge_address = self.get_gauge_address()
        self.total_vote_power = 0
        self.voter_count = 0
        
        self.relative_vote_power = 0
        self.votes_per_dollar = 0
        self.price_per_vote = 0
        
        self.get_meta()
        

    def update_derrived_stats(self, relative_bounty_weight):
        self.relative_vote_power = relative_bounty_weight * self.total_vote_power
        if self.bounty_value > 100 and self.relative_vote_power >100:
            self.votes_per_dollar = self.relative_vote_power / self.bounty_value 
            self.price_per_vote = self.bounty_value / self.relative_vote_power


    def get_gauge_ref(self):
        if self.period in convex_snapshot_proposal_choice_map:
            if self.choice_index < len(convex_snapshot_proposal_choice_map[self.period]):
                return convex_snapshot_proposal_choice_map[self.period][self.choice_index]
            else:
                pass
                # print("_"*50)
                # print (self.period)
                # print (len(convex_snapshot_proposal_choice_map[self.period]))
        return "Not Found"
        
    def get_gauge_address(self):
        try: 
            gauge_address = gauge_registry.get_gauge_address_from_snapshot(self.gauge_ref)
        except:
            gauge_address = "0xNotFound"
        return gauge_address

    def get_meta(self):
        try:
            df_aggs = df_vote_aggregates[(df_vote_aggregates['period']== self.period) & 
                                    (df_vote_aggregates['choice']== self.gauge_ref)]
            self.total_vote_power = df_aggs.iloc[0]['total_vote_power']
            self.voter_count = df_aggs.iloc[0]['vlcvx_voter_count']
            # self.period = df_aggs.iloc[0]['period']
            self.period_end_date = df_aggs.iloc[0]['period_end_date']
        except Exception as e:
            try:
                df_aggs = df_vote_aggregates[(df_vote_aggregates['period']== self.period) ]
                # self.period = df_aggs.iloc[0]['period']
                self.period_end_date = df_aggs.iloc[0]['period_end_date']
            except Exception as e:
                pass
                # print(self.period)
                # print(self.gauge_ref)
                # # print(df_vote_aggregates['choice'])
                # print(e)
                # print(traceback.format_exc())


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
            'relative_vote_power': self.relative_vote_power,
        }
    # def fill_in(self, proposals):
    #     proposals.search
    #     proposals = df_vote_aggregates[df_vote_aggregates['proposal_end'] == current_period]
        


def get_df_bounty_for_round():
    filename = 'votium_bounty_for_round' #+ current_file_title
    resp_dict = read_csv(filename, 'source')
    df_stakedao_events_created = pd.json_normalize(resp_dict)
    return df_stakedao_events_created.sort_values("block_timestamp", axis = 0, ascending = True)

def get_df_bounty_formatted(vbr, df):
    # vbr = VBRegistry()
    vbr.process_bounties(df)
    temp = vbr.format_output()
    # print(temp)
    df_bounty_formatted = pd.json_normalize(temp)
    df_bounty_formatted = df_bounty_formatted[(df_bounty_formatted['block_timestamp'] > "2022-12-18")]

    return df_bounty_formatted.sort_values("block_timestamp", axis = 0, ascending = False)


def update_snapshot_vote_choice(vbr, raw_df = None):
    if not isinstance(raw_df, type(None)):
        df_convex_snapshot_vote_choice =  raw_df
    else:
        df_convex_snapshot_vote_choice = app.config['df_convex_snapshot_vote_choice']

    df_convex_snapshot_vote_choice['bounties_eligible'] = vbr.get_bounty_paid(
        df_convex_snapshot_vote_choice['period'], 
        df_convex_snapshot_vote_choice['choice_index'],
        df_convex_snapshot_vote_choice['choice_power']
        )   
    
    df_convex_snapshot_vote_choice['bounty_currencies'] = vbr.get_bounty_currency(
        df_convex_snapshot_vote_choice['period'], 
        df_convex_snapshot_vote_choice['choice_index']
        )   

    if not isinstance(raw_df, type(None)):
        return df_convex_snapshot_vote_choice
    else:
        app.config['df_convex_snapshot_vote_choice'] = df_convex_snapshot_vote_choice

def update_snapshot_aggregates(vbr, raw_df=None):
    if not isinstance(raw_df, type(None)):
        df_convex_snapshot_vote_aggregates =  raw_df
    else:
        df_convex_snapshot_vote_aggregates = app.config['df_convex_snapshot_vote_aggregates']

    df_convex_snapshot_vote_aggregates['bounties_total'] = vbr.get_bounty_aggregate(
        df_convex_snapshot_vote_aggregates['period'], 
        df_convex_snapshot_vote_aggregates['choice_index']
        )   
    
    df_convex_snapshot_vote_aggregates['bounty_currencies'] = vbr.get_bounty_currency(
        df_convex_snapshot_vote_aggregates['period'], 
        df_convex_snapshot_vote_aggregates['choice_index']
        )  
    if not isinstance(raw_df, type(None)):
        return df_convex_snapshot_vote_aggregates
    else:    
        app.config['df_convex_snapshot_vote_aggregates'] = df_convex_snapshot_vote_aggregates


votium_bounty_registry = VBRegistry()
df_bounty_for_round = get_df_bounty_for_round()
df_votium_bounty_formatted = get_df_bounty_formatted(votium_bounty_registry, df_bounty_for_round)

try:
    app.config['df_votium_bounty_formatted'] = df_votium_bounty_formatted
    app.config['votium_bounty_registry'] = votium_bounty_registry
    try:
        update_snapshot_vote_choice(votium_bounty_registry)
        update_snapshot_aggregates(votium_bounty_registry)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
except:
    print("could not register in app.config\n\tVotium Bounties")

# print(df_bounty_formatted.head())