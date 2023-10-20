from flask import current_app as app

# from ... import db
from app.data.local_storage import (
    pd,
    read_json, 
    read_csv,  
    write_dataframe_csv,
    write_dfs_to_xlsx
    )


# filename = 'crv_locker_logs'

import ast
from datetime import datetime as dt

from app.utilities.utility import get_period, get_period_end_date
from app.data.reference import ( 
    known_large_curve_holders, 
    gauge_names, 
    gauge_symbols,  
    current_file_title,
    fallback_file_title,
)


class BRegistry():
    def __init__(self):
        self.bounty_map = {}

    def process_creation(self, df):
        self.process_general(df, 'create')

    def process_increase(self,df):
        self.process_general(df, 'increase')

    def process_closed(self, df):
        self.process_general(df, 'close')

    def process_claims(self, df):
        self.process_general(df, 'claim')

    def process_general(self, df, tag):
        for index, row in df.iterrows():
            self.process_row(row, tag)

    def process_row(self, row, tag):
        if 'ID' in row:
            this_id = row['ID']
        elif 'BRIBE_ID' in row:
            this_id = row['BRIBE_ID']
        else:
            return
        if not this_id in self.bounty_map:
            self.bounty_map[this_id] = Bounty(this_id)
        bounty = self.bounty_map[this_id]
        if tag == 'create':
            bounty.create(row)
        elif tag == 'increase':
            bounty.increase(row)
        elif tag == 'close':
            bounty.close_bounty(row)
        elif tag == 'claim':
            bounty.claim(row)
        else:
            return
        return True
    
    def format_bounties(self):
        all_out = []
        for key in self.bounty_map:
            try:
                b = self.bounty_map[key]
                out = {
                    'bounty_id': key,
                    'gauge': b.creation.gauge,
                    'gauge_name': b.creation.gauge_name,
                    'gauge_symbol': b.creation.gauge_symbol,
                    'number_of_periods': b.num_periods_list[-1],
                    'total_reward_amount': b.total_reward_amount_list[-1],
                    'start_timestamp': b.creation.block_timestamp
                }
                all_out.append(out)
            except Exception as e:
                # print(e)
                pass
        return all_out
    
    def format_claims(self):
        all_out = []
        for key in self.bounty_map:
            b = self.bounty_map[key]
            for claim in b.claims:
                try:
                    claim.format_output()
                    out = {
                        'gauge': b.creation.gauge,
                        'gauge_name': b.creation.gauge_name,
                        'gauge_symbol': b.creation.gauge_symbol,
                        'number_of_periods': b.num_periods_list[-1],
                        'total_reward_amount': b.total_reward_amount_list[-1],
                    }
                    temp = {**out, **claim.format_output()}
                    all_out.append(temp)
                except Exception as e:
                    # print(e)
                    pass
        return all_out 
    
    # def format_claims(self, )





class Bounty():
    def __init__(self, id):
        self.id = id
        self.creation = None
        self.increases = []
        self.claims = []
        self.claims_map = {}    # period , address, []
        self.close = None
        self.round = None  # NEED TO FIGURE THIS PART OUT
        self.gauge_name = None

        self.num_periods_list = []
        self.total_reward_amount_list = []
        self.remaining_reward_amount = 0
        self.claimed_amount_map = {} # period, int

    # def format_output(self):
    #     output_data = []
    #     for address in self.claims_map:
    #         total_claimed =


    
    def create(self, row):
        self.creation = BCreated(row)
        self.gauge_name = self.creation.gauge_name
        self.num_periods_list.append(self.creation.number_of_periods)
        self.total_reward_amount_list.append(self.creation.total_reward_amount)
        self.remaining_reward_amount = self.total_reward_amount_list[-1]
    
    def increase(self, row):
        increase = BIncreased(row)
        self.increases.append(increase)
        self.total_reward_amount_list.append(increase.total_reward_amount)

    def close_bounty(self, row):
        self.close = BClosed(row)

    def claim(self, row):
        claim = BClaimed(row)
        self.claims.append(claim)
        if not claim.period in self.claims_map:
            self.claims_map[claim.period] = {}
        claim_round_map = self.claims_map[claim.period]

        if not claim.user in claim_round_map:
            claim_round_map[claim.user] = []
        claim_round_map[claim.user].append(claim)
        
        if not claim.period in self.claimed_amount_map:
            self.claimed_amount_map[claim.period] = 0
        if claim.amount and len(claim.amount) > 4:
            self.claimed_amount_map[claim.period] += int(claim.amount)
            



class BCreated():
     def __init__(self, row):
        self.event_name = row['EVENT_NAME'] 
        self.contract_address = row['CONTRACT_ADDRESS'] 
        # Decoded Log Expanded
        self.id = row['ID'] 
        self.gauge = row['GAUGE'] 
        self.is_upgradeable = row['IS_UPGRADEABLE']
        self.manager = row['MANAGER'] 
        self.max_reward = row['MAX_REWARD'] 
        self.number_of_periods = row['NUMBER_OF_PERIODS'] 
        self.reward_token = row['REWARD_TOKEN']
        self.total_reward_amount = row['TOTAL_REWARD_AMOUNT'] 
        # Context
        self.reward_name = row['REWARD_NAME'] 
        self.reward_symbol = row['REWARD_SYMBOL'] 
        self.gauge_name = row['GAUGE_NAME'] 
        self.gauge_symbol = row['GAUGE_SYMBOL']  
        # Basic
        self.decoded_log = row['DECODED_LOG'] 
        self.block_timestamp = row['BLOCK_TIMESTAMP'] 
        self.block_number = row['BLOCK_NUMBER']   




class BIncreased():
    def __init__(self, row):
        self.event_name = row['EVENT_NAME']
        self.contract_address = row['CONTRACT_ADDRESS'] 
        # Decoded Log Expanded
        self.id = row['ID'] 
        self.max_reward = row['MAX_REWARD']
        self.number_of_periods = row['NUMBER_OF_PERIODS']
        self.total_reward_amount = row['TOTAL_REWARD_AMOUNT']
        # Basic
        self.decoded_log = row['DECODED_LOG']
        self.block_timestamp = row['BLOCK_TIMESTAMP']
        self.block_number = row['BLOCK_NUMBER']


class BClosed():
    def __init__(self, row):
        self.event_name = row['EVENT_NAME']
        self.contract_address = row['CONTRACT_ADDRESS'] 
        # Decoded Log Expanded
        self.id = row['ID'] 
        self.remaining_reward = row['REMAININGREWARD']
        # Basic
        self.decoded_log = row['DECODED_LOG']
        self.block_timestamp = row['BLOCK_TIMESTAMP']
        self.block_number = row['BLOCK_NUMBER']



class BClaimed():
    def __init__(self, row):
        self.event_name = row['EVENT_NAME']
        self.contract_address = row['CONTRACT_ADDRESS'] 
        # Decoded Log Expanded
        self.id = row['BRIBE_ID'] 
        self.amount = row['AMOUNT'] 
        self.period = row['PERIOD']
        self.protocol_fees = row['PROTOCOL_FEES'] 
        self.reward_token = row['REWARD_TOKEN'] 
        self.user = row['USER'] 
        # Context
        self.user_label = row['USER_LABEL']
        self.user_name = row['USER_NAME'] 
        self.user_contract_name = row['USER_CONTRACT_NAME'] 
        # Basic
        self.decoded_log = row['DECODED_LOG']
        self.block_timestamp = row['BLOCK_TIMESTAMP']
        self.block_number = row['BLOCK_NUMBER']

    def format_output(self):
        return {
            'event_name': self.event_name,
            'contract_address': self.contract_address,
            'bountiy_id': self.id,
            'amount': self.amount,
            'period': self.period,
            'protocol_fees': self.protocol_fees,
            'reward_token': self.reward_token,
            'user': self.user,
            'user_label': self.user_label,
            'user_name': self.user_name,
            'user_contract_name': self.user_contract_name,
            'decoded_log': self.decoded_log,
            'block_timestamp': self.block_timestamp,
            'block_number': self.block_number,
        }
    


def get_df_bounty_created():
    filename = 'stake_dao_bounty_created_' + current_file_title
    resp_dict = read_csv(filename, 'source')
    df_stakedao_events_created = pd.json_normalize(resp_dict)
    return df_stakedao_events_created.sort_values("BLOCK_TIMESTAMP", axis = 0, ascending = True)

def get_df_bounty_duration_increased():
    filename = 'stake_dao_bounty_duration_increased_' + current_file_title
    resp_dict = read_csv(filename, 'source')
    df_stakedao_events_duration_increase = pd.json_normalize(resp_dict)
    return df_stakedao_events_duration_increase.sort_values("BLOCK_TIMESTAMP", axis = 0, ascending = True)


def get_df_bounty_claimed():
    filename = 'stake_dao_bounty_claimed_' + current_file_title
    resp_dict = read_csv(filename, 'source')
    df_stakedao_events_claimed = pd.json_normalize(resp_dict)
    return df_stakedao_events_claimed.sort_values("BLOCK_TIMESTAMP", axis = 0, ascending = True)

def get_df_bounty_closed():
    filename = 'stake_dao_bounty_closed_' + current_file_title
    resp_dict = read_csv(filename, 'source')
    df_stakedao_events_closed = pd.json_normalize(resp_dict)
    return df_stakedao_events_closed.sort_values("BLOCK_TIMESTAMP", axis = 0, ascending = True)



df_stakedao_bounty_created = get_df_bounty_created()
df_stakedao_bounty_duration_increase = get_df_bounty_duration_increased()
df_stakedao_bounty_claimed = get_df_bounty_claimed()
df_stakedao_bounty_closed = get_df_bounty_closed()


registry = BRegistry()
registry.process_creation(df_stakedao_bounty_created)
registry.process_increase(df_stakedao_bounty_duration_increase)
registry.process_claims(df_stakedao_bounty_claimed)
registry.process_closed(df_stakedao_bounty_closed)


