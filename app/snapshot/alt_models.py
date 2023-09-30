import pandas as pd
# import os
from datetime import datetime as dt
import numpy as np



from app.utilities.utility import get_period, get_period_end_date, get_period_direct
from app.data.reference import known_large_cvx_holders_addresses
from app.curve.gauges.models import gauge_registry

from app.data.snapshot_api import get_space, get_proposals, get_votes

from app.data.local_storage import (
    read_json,
    read_csv,
    csv_to_df
)

print("Loading... { snapshot.alt_models }")


class SnapshotAsSource():
    def __init__(self, space_address, first, skip, target = None):
        self.space = get_space(space_address)
        self.proposals = self.get_proposals(first, skip)
        self.target = None # Target Proposal
        self.proposal_choice_map = {}
        self.processed_votes = self.process_votes()

    def get_proposals(self, first, skip):
        proposals = get_proposals(self.space['id'], first, skip)
        df_proposals = pd.json_normalize(proposals)
        # Filter for proposals that matter
        if self.space['id'] == 'sdcrv.eth':
            print('stakedao!')
            local_df_proposals = df_proposals[
                df_proposals['title'].str.startswith('Gauge vote') &
                df_proposals['title'].str.contains('CRV')
                ]
        else:
            local_df_proposals = df_proposals[df_proposals['title'].str.contains('Gauge Weight')]
        local_df_proposals = local_df_proposals[~local_df_proposals['title'].str.contains('TEST')]
        
        local_df_proposals = local_df_proposals.sort_values('start')
        return local_df_proposals


    def process_votes(self):
        total_output = []
        for i, proposal in self.proposals.iterrows():
            if self.target:
                if not proposal['title'] == self.target:
                    # "Could not find title"
                    continue
            votes = get_votes(proposal['id'])
            df_votes = pd.json_normalize(votes)
            # normalize addresses to all lowercase
            df_votes['voter'] = df_votes['voter'].str.lower()
            output = self.generate_output(proposal, df_votes)
            total_output = total_output + output
        return total_output


    def get_choice_percent(self, choice_weight, total_weight):
        # print(self.total_vote_weight)
        if total_weight > 0:
            return choice_weight / total_weight
        else:
            return choice_weight

    def get_known_as(self, voter_address):
        if not voter_address in known_large_cvx_holders_addresses:
            return '_'    
        else: 
            return known_large_cvx_holders_addresses[voter_address]
      

    def generate_output(self, this_proposal, df_votes):
        output = []
        start_time =  dt.fromtimestamp(this_proposal.start) #.strftime('%Y-%m-%d %H:%M:%S')
        end_time =  dt.fromtimestamp(this_proposal.end) #.strftime('%Y-%m-%d %H:%M:%S')
        period_end_date =  get_period_end_date(end_time)
        period = get_period_direct(end_time)
        self.proposal_choice_map[period] = this_proposal.choices
        # Iterate through voters
        for index, row in df_votes.iterrows():
            total_weight = 0
            options_voted = {}
            for i, choice in enumerate(this_proposal.choices):
                vote_key = f"choice.{i+1}"
                if vote_key in row:
                    if not np.isnan(row[vote_key]):
                        # print(choice)
                        # print(row[vote_key])
                        total_weight += row[vote_key]
                        options_voted[i+1] = row[vote_key]

            # Generate Row per Option
            for key in options_voted:
                choice = this_proposal.choices[key - 1]
                choice_weight = options_voted[key]  

                known_as = self.get_known_as(row['voter'])
                choice_percent = self.get_choice_percent(choice_weight, total_weight)

                timestamp =  dt.fromtimestamp(row['created']) #.strftime('%Y-%m-%d %H:%M:%S')

                output.append({
                            'proposal_title': this_proposal.title,
                            'voter': row['voter'],
                            'known_as': known_as,
                            'choice': choice,
                            'choice_index': key,
                            'voting_weight': choice_weight,
                            'total_weight': total_weight,
                            'choice_percent': choice_percent,
                            'available_power': row['vp'],
                            'choice_power': float( choice_percent * row['vp']), 
                            'timestamp': timestamp,
                            'proposal_start': start_time,
                            'proposal_end': end_time,
                            'period_end_date':  period_end_date,
                            'period': period,
                            'valid': start_time < end_time,
                            'vote_id': row['id'],
                            'gauge_addr': gauge_registry.get_gauge_address_from_snapshot(choice)
                        })
                

        return output
    
    def get_vote_df(self):
        return pd.json_normalize(self.processed_votes)
    
    def get_proposal_choice_map_df(self):
        return pd.json_normalize([self.proposal_choice_map])
    

def format_df_snapshot_from_snapshot(df):
    df['choice_index'] = df['choice_index'].astype(int)
    df['voting_weight'] = df['voting_weight'].astype(float)
    df['total_weight'] = df['total_weight'].astype(float)
    df['choice_percent'] = df['choice_percent'].astype(float)
    df['available_power'] = df['available_power'].astype(float)
    df['choice_power'] = df['choice_power'].astype(float)
    df['valid'] = df['valid'].astype(bool)
    df['period_end_date'] = pd.to_datetime(df['period_end_date']).dt.date
    return df


def get_df_snapshot_from_snapshot(target):
    try:
        filename = (f"{target}_snapshot_from_snapshot")
        temp = csv_to_df(filename)
        temp = format_df_snapshot_from_snapshot(temp)
        return temp
    except:
        return []

def def_get_proposal_choice_map(target):
    try:
        filename = (f"{target}_snapshot_proposal_choice_map")
        temp = csv_to_df(filename).to_dict()
        output = {}
        for key in temp.keys():
            value = temp.iloc[0][key]
            value = value[1:-1].replace("'", "").split(',')
            output[key] = value
        return output
    except:
        return []   

    

def merge_target(df_snapshot, proposal_choice_map, target):
    local_df_snapshot = get_df_snapshot_from_snapshot(target)
    # if no data return untouched
    if not len(local_df_snapshot) > 0:
        return df_snapshot, proposal_choice_map
    else:
        local_proposal_choice_map = def_get_proposal_choice_map(target)
    # clear out overlap
    for title in local_df_snapshot.proposal_title.unique():
        # print(f"Removing: {title}")
        df_snapshot = df_snapshot[~df_snapshot['proposal_title'].str.match(title)]
    # merge the things
    df_snapshot = pd.concat([df_snapshot, local_df_snapshot])
    proposal_choice_map.update(local_proposal_choice_map)
    return df_snapshot, proposal_choice_map