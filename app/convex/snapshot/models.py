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
    current_file_title,
    fallback_file_title,
)

import traceback


from app.data.reference import known_large_cvx_holders_addresses

class Snapshot():
    def __init__(self):
        self.networks = {}
        self.spaces ={}

    def process(self, df):
        for index, row in df.iterrows():
            # find network
            if 'NETWORK' in row:
                if not row['NETWORK'] in self.networks:
                    n = Network(row['NETWORK'])
                    self.networks[n.network] = n
                else:
                    n = self.networks[row['NETWORK']]
                # get space
                s = n.new_space(n, row)
                s.process_row(row)


    def vote_power(self, network_id, space_id, size=20):
        x = -1
        space = self.networks[network_id].spaces[space_id]

        title = space.gauge_list[x].proposal_title
        num_voters = len(space.gauge_list[x].votes)

        data = { 'voter': [],
                'voting_power': [],
                'proposal_start_time': [],
                'proposal_title': [],
                }
        i = 1
        while i <= size:
            x = -i
            for v_address in space.gauge_list[x].votes:
                p = space.gauge_list[x]
                v = space.gauge_list[x].votes[v_address]
                data['voter'].append(v_address)
                data[f'voting_power'].append(v.voting_power)
                data['proposal_start_time'].append(p.proposal_start_time)
                data['proposal_title'].append(p.proposal_title)
            i+= 1
        return pd.DataFrame.from_dict(data)


    def vote_count(self, network_id, space_id, size = 20):
        space = self.networks[network_id].spaces[space_id]

        data_alt = {'num_voters': [],
                    'proposal_start_time': [],
                    'proposal_title': [],
                    }
        i = 1
        while i <= size:
            x = -i
            p = space.gauge_list[x]
            num_votes = len(space.gauge_list[x].votes)

            data_alt['proposal_start_time'].append(p.proposal_start_time)
            data_alt['num_voters'].append(num_votes)
            data_alt['proposal_title'].append(p.proposal_title)

            i+= 1
        return pd.DataFrame.from_dict(data_alt)

    def format_delta_output(self):
        output_data = []
        for network_name in self.networks:
            network = self.networks[network_name]
            for space_name in network.spaces:
                space = network.spaces[space_name]
                for voter_address in space.voters:
                    voter = space.voters[voter_address]
                    for proposal in voter.vote_change_per_gauge_proposal:
                        row_of_data = voter.vote_change_per_gauge_proposal[proposal]
                        if row_of_data:
                            output_data.append(row_of_data)
        return output_data
    
    def format_final_choice_output(self):
        output_data = []
        for network_name in self.networks:
            network = self.networks[network_name]
            for space_name in network.spaces:
                space = network.spaces[space_name]
                for proposal_id in space.proposals:
                    proposal = space.proposals[proposal_id]
                    for voter in proposal.voter_choices:
                        vote = proposal.voter_choices[voter]
                        if vote:
                            for choice in vote.choices:
                                if choice:
                                    output_data.append(choice.format_output())
        return output_data


    def format_choice_output(self):
        output_data = []
        for network_name in self.networks:
            network = self.networks[network_name]
            for space_name in network.spaces:
                space = network.spaces[space_name]
                for voter_address in space.voters:
                    voter = space.voters[voter_address]

                    for choice in voter.choices:
                        if choice:
                            output_data.append(choice.format_output())
        return output_data




class Network():
    def __init__(self, network):
        self.network = network
        self.spaces = {}

    def new_space(self, network, row):
        if 'SPACE_ID' in row:
            if not row['SPACE_ID'] in self.spaces:
                s = Space(network, row['SPACE_ID'])
                self.spaces[s.space_id] = s
            else:
                s = self.spaces[row['SPACE_ID']]
        return s


class Space():
    def __init__(self, network, space_id):
        self.network = network
        self.space_id = space_id

        self.proposals = {}
        self.voters = {}

        self.proposal_list = []
        self.gauge_list = []
        self.gauge_map = {}

    def process_row(self, row):
        # update space primatives
        p = self.new_proposal(row)
        v = self.new_voter(row)
        # set vote
        self.process_vote(p, v, row)


    def new_proposal(self, row):
        if 'PROPOSAL_ID' in row:
            if not row['PROPOSAL_ID'] in self.proposals:
                p = Proposal(self, row)
                self.proposals[p.proposal_id] = p
                self.proposal_list.append(p)
                if 'Gauge Weight' in p.proposal_title and not 'TEST' in p.proposal_title:
                    self.gauge_list.append(p)
                    self.gauge_map[p.proposal_id] = p
                    
            else:
                p = self.proposals[row['PROPOSAL_ID']]
                
            return p
        return None
    
    def new_voter(self,row):
        if 'VOTER' in row:
            if not row['VOTER'] in self.voters:
                v = Voter(self, row)
                self.voters[v.address] = v
            else:
                v = self.voters[row['VOTER']]
            return v
        return None
    
    def process_vote(self, p, voter, row):
        if p:
            vote = p.new_vote(voter, row)
        

class Proposal():
    def __init__(self, space, row):
        self.space = space
        self.proposal_id = row['PROPOSAL_ID']
        self.proposal_author = row['PROPOSAL_AUTHOR']
        self.proposal_title = row['PROPOSAL_TITLE']
        self.proposal_text = row['PROPOSAL_TEXT']
        self.delay = row['DELAY']
        self.quorum = row['QUORUM']
        self.vote_option = row['VOTE_OPTION']
        self.choices = row['CHOICES']
        self.voting_period = row['VOTING_PERIOD']
        self.proposal_start_time = row['PROPOSAL_START_TIME']
        self.proposal_end_time = row['PROPOSAL_END_TIME']
        self.fails_logged = 0
        self.votes = {}
        self.vote_id = 0
        self.voter_choices = {}


    def new_vote(self, voter, row):
        if voter:
            vote = Vote(self, voter, row, vote_id = self.vote_id)
            self.vote_id += 1
            self.votes[voter.address] = vote
            voter.new_vote(vote)
            if vote.is_valid():
                if vote.voter in self.voter_choices:
                    current_vote = self.voter_choices[vote.voter]
                    if current_vote.vote_id < vote.vote_id:
                        self.voter_choices[vote.voter] = vote
                else:
                    self.voter_choices[vote.voter] = vote
            return vote
        return None
    

    # def get_choices(self):
    #     choices = self
    # def run_calcs(self):
    #     num_voters = len(self.)

class Voter():
    def __init__(self, space, row):
        self.space = space
        self.address = row['VOTER']
        self.address_name = row['ADDRESS_NAME']
        
        self.label_type = row['LABEL_TYPE']
        self.label_subtype = row['LABEL_SUBTYPE']
        self.label = row['LABEL']

        self.votes = {}
        self.votes_per_proposal = {}
        self.vote_change_per_gauge_proposal = {}

        self.choices = []
        if self.address in known_large_cvx_holders_addresses:
            self.known_as = known_large_cvx_holders_addresses[self.address]
        else:
            self.known_as = "_"
        self.vote_id = 0

    def new_vote(self, vote):
        p = vote.proposal
        self.votes[p.proposal_id] = vote
        if not p.proposal_id in self.votes_per_proposal:
            self.votes_per_proposal[p.proposal_id] = []
        self.votes_per_proposal[p.proposal_id].append(vote)
        if p.proposal_id in p.space.gauge_map:
            # print("GAUGE VOTE FOUND")
            self.vote_change_per_gauge_proposal[p.proposal_id] = self.calc_vote_change_per_proposal(vote)
        # else:
            # print(f"NO Gauge Vote for {p.proposal_title}")


### ISSUE HERE RECOGNIZING GAUGE VS NON GAUGE FILTERING

    def calc_vote_change_per_proposal(self, vote):
        p_list = self.space.gauge_list 
        if vote.proposal.proposal_id in p_list:
            x = p_list.index(vote.proposal.proposal_id)
        else:
            x = len(p_list)
        if x > 0:
            last_proposal_id = p_list[x-1]
        else:
            last_proposal_id = None
        try:
            last_vote = self.votes_per_proposal[last_proposal_id][-1]
        except:
            last_vote = None
        output = {}
        this_vote_by_choice = vote.get_vote_options()
        # print(this_vote_by_choice)
        try:
            if last_vote:
                last_vote_by_choice = last_vote.get_vote_options()
                for choice in last_vote_by_choice:
                    # print("here")
                    # if choice == 'eUSD+FRAXBP (0xAEda…)':
                        # print(f'FOUND {choice}')
                    # print(choice)
                    if this_vote_by_choice:
                        if choice in this_vote_by_choice:
                            output[choice] = {
                                'choice': choice,
                                'voter_addresss': self.address,
                                'proposal_id': vote.proposal.proposal_id,
                                'proposal_start_time': vote.proposal.proposal_start_time,
                                'proposal_end_time': vote.proposal.proposal_end_time,
                                'vote_power': this_vote_by_choice[choice]['vote_power'],
                                'vote_percent': this_vote_by_choice[choice]['vote_percent'],
                                'delta_percent': this_vote_by_choice[choice]['vote_percent'] - last_vote_by_choice[choice]['vote_percent'],
                                'delta_power': this_vote_by_choice[choice]['vote_power'] - last_vote_by_choice[choice]['vote_power'],
                                'available_power': this_vote_by_choice[choice]['available_power'],
                            }
                        else:
                            # print("here2")
                            # if choice == 'eUSD+FRAXBP (0xAEda…)':
                                # print(f'FOUND2 {choice}')
                            keys = this_vote_by_choice.keys()
                            alt_choice = this_vote_by_choice[keys[0]]
                            output[choice] = {
                                'choice': choice,
                                'voter_addresss': self.address,
                                'proposal_id': vote.proposal.proposal_id,
                                'proposal_start_time': vote.proposal.proposal_start_time,
                                'proposal_end_time': vote.proposal.proposal_end_time,
                                'vote_power': 0,
                                'vote_percent': 0,
                                'delta_percent': last_vote_by_choice[choice]['vote_percent'] * -1,
                                'delta_power': last_vote_by_choice[choice]['vote_power'] * - 1,
                                'available_power': alt_choice[choice]['available_power'],
                                }                 

            else:
                if this_vote_by_choice:
                    for choice in this_vote_by_choice:
                        # print("here3")
                        # if choice == 'eUSD+FRAXBP (0xAEda…)':
                            # print(f'FOUND3 {choice}')
                        # print(this_vote_by_choice[choice])
                        output[choice] = {
                            'choice': choice,
                            'voter_addresss': self.address,
                            'proposal_id': vote.proposal.proposal_id,
                            'proposal_start_time': vote.proposal.proposal_start_time,
                            'proposal_end_time': vote.proposal.proposal_end_time,
                            'vote_power': this_vote_by_choice[choice]['vote_power'],
                            'vote_percent': this_vote_by_choice[choice]['vote_percent'],
                            'delta_percent': this_vote_by_choice[choice]['vote_percent'],
                            'delta_power': this_vote_by_choice[choice]['vote_power'],
                            'available_power': this_vote_by_choice[choice]['available_power'],
                        }  
                else:
                    print(this_vote_by_choice)
                    print("Not Found")
                    print("___________")
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            print('failed')
        # if not output:
        #     print(last_vote)            
        return output


class Vote():
    def __init__(self, proposal, voter, row, vote_id):
        self.proposal = proposal
        self.voter = voter
        self.vote_id = vote_id
        self.vote_option = row['VOTE_OPTION']
        self.voting_power = row['VOTING_POWER']
        self.vote_timestamp = row['VOTE_TIMESTAMP']
        self.choices = []
        self.process_choices()

    def process_choices(self):
        self.choices = []
        options = self.get_vote_options_new()
        # print(options)
        choices = self.get_vote_choices()
        # print(choices)
        if not options or not choices:
            print("Error")
            return None
        
        if type(options) == dict:
            total_weight = 0
            for key in options.keys():
                # print(key)
                # if int(key) == 138:
                    # print('HURRAY')
                if int(key) <= len(choices):
                    choice = choices[int(key)-1]
                else:
                    print(f'key {key} not found in choices: {len(choices)}')
                    continue
                # print(choice)
                option = options[key]
                weight = int(option)
                total_weight += weight
                this_choice = Choice(self,
                                     self.proposal, 
                                     self.voter, 
                                     choice, 
                                     int(key),
                                     weight, 
                                     self.voting_power, 
                                     self.vote_timestamp,
                                     self.vote_id)
                self.voter.choices.append(this_choice)
                self.choices.append(this_choice)
            for choice in self.choices:
                choice.set_total_vote_weight(total_weight)
        elif type(options) == list:
            total_weight = 0
            for index, option in enumerate(options):
                if index < len(choices):
                    # maybe do stuff here
                    choice = choices[index]
                    print(f'key {index}  of {len(options)} found in choices {len(choices)}')
                    pass
                else:
                    print(f'\tkey {index} of {len(options)} not found in choices: {len(choices)}')
                    print(index)
                    print(choices)
                    continue    
                if option == 'NA':
                    weight = 0
                else:
                    weight = float(option)
                total_weight += weight
                this_choice = Choice(
                    self,
                    self.proposal, 
                    self.voter, 
                    choice, 
                   int(index),  #choice_id
                    weight, 
                    self.voting_power, 
                    self.vote_timestamp,
                    self.vote_id
                )
                self.voter.choices.append(this_choice)
                self.choices.append(this_choice)
            for choice in self.choices:
                choice.set_total_vote_weight(total_weight)
        else:
            print("unexpected options")
            print(options)

    def get_vote_choices(self):
        try:
            # ['["cDAI+cUSDC (0xA2B4…)","cDAI+cUSDC+USDT (0x52EA…)"
            if self.proposal.choices[0][0] == '[':
                choices = ast.literal_eval(self.proposal.choices[0])
            else:
                choices = self.proposal.choices
        except Exception as e:
            if self.proposal.fails_logged < 3:
                print("== Failed")
                print("\tproposal")
                print(self.proposal.proposal_title)
                print(self.proposal.choices)
                print(type(self.proposal.choices))
                print("\tvote")
                print(traceback.format_exc())
            self.proposal.fails_logged += 1
            return None        
        return choices
        
    def get_vote_options_new(self):
        try:
            if self.vote_option[0][0] == '[' or self.vote_option[0][0] == '{':
                options = ast.literal_eval(self.vote_option[0])
            else:
                options = self.vote_option
        except Exception as e:
            if self.proposal.fails_logged < 3:
                print("== Failed")
                print("\tproposal")
                print(self.proposal.proposal_title)
                print("\tvote")
                print(self.vote_option)
                print(type(self.vote_option))
                print(traceback.format_exc())
            self.proposal.fails_logged += 1
            return None        
        return options
        

    def get_vote_options(self):
        try:
            # ['["cDAI+cUSDC (0xA2B4…)","cDAI+cUSDC+USDT (0x52EA…)"
            if self.vote_option[0][0] == '[' or self.vote_option[0][0] == '{':
                options = ast.literal_eval(self.vote_option[0])
            else:
                options = self.vote_option

            if self.proposal.choices[0][0] == '[':
                choices = ast.literal_eval(self.proposal.choices[0])
            else:
                choices = self.proposal.choices
        except Exception as e:
            if self.proposal.fails_logged < 1:
                print("== Failed")
                print("\tproposal")
                print(self.proposal.proposal_title)
                print(self.proposal.choices)
                print(type(self.proposal.choices))
                print("\tvote")

                print(self.vote_option)
                print(type(self.vote_option))
                print(traceback.format_exc())
            self.proposal.fails_logged += 1
            return None
        if not options or not choices:
            return None
        output = {}
        try:
            if type(options) == dict:
                for key in options.keys():
                    if int(key) < len(choices):
                        c = choices[int(key)]
                    else:
                        # print(f'key {key} not found in choices: {len(choices)}')
                        # print(self.proposal.proposal_title)
                        continue
                    # print(c)
                    o = options[key]
                    percent = int(o) #/ 1000
                    output[c] = {'vote_percent': percent,
                                'vote_power': percent * float(self.voting_power),
                                'available_power': float(self.voting_power),
                                }
            else:
                i = -1
                while i < len(choices)-1:
                    i+=1
                    if i >= len(options):
                        break
                    o = options[i]
                    if o == 'NA':
                        continue
                    c = choices[i]

                    percent = float(o) / 1000
                    output[c] = {'vote_percent': percent,
                                'vote_power': percent * float(self.voting_power),
                                'available_power': float(self.voting_power),
                                }     
        except Exception as e:
            if self.proposal.fails_logged < 3:
                print("== Failed")
                print("\tproposal")
                print(self.proposal.proposal_title)
                print(f"O: {len(options)} || {options}")
                print(f"C: {len(choices)} || {choices}")
                print(traceback.format_exc())
                print(e)
            self.proposal.fails_logged += 1
            return None   
        # print(output)
        return output

    def is_valid(self):
        vote_time = dt.strptime(self.vote_timestamp,'%Y-%m-%d %H:%M:%S.%f')
        start_time = dt.strptime(self.proposal.proposal_start_time,'%Y-%m-%d %H:%M:%S.%f')
        end_time = dt.strptime(self.proposal.proposal_end_time,'%Y-%m-%d %H:%M:%S.%f')
        # end_time = dt(temp_end.year, temp_end.month, temp_end.day)
        if vote_time >= start_time: 
            if vote_time < end_time:
                # if self.voter.known_as == 'Votium':
                #     print( self.proposal.proposal_title)
                #     print (f"start {start_time}")
                #     print (f"end {end_time}")
                #     print (f"vote {vote_time}")
                #     print ("_"* 100)
                return True
        return False

class Choice():
    def __init__(self,vote,  proposal, voter, choice, choice_id, weight, power, ts, vote_id):
        self.vote = vote
        self.proposal = proposal
        self.voter = voter
        self.choice = choice
        self.choice_id = choice_id
        self.voting_weight = float(weight)
        self.available_power = float(power)
        self.ts = ts
        self.total_vote_weight = 1
        self.vote_id = vote_id

    def choice_percent(self):
        # print(self.total_vote_weight)
        if self.total_vote_weight > 0:
            return self.voting_weight / self.total_vote_weight
        else:
            return 0
    
    def choice_power(self):
        return float( self.choice_percent() * self.available_power)

    def set_total_vote_weight(self, total_vote_weight):
        self.total_vote_weight = float(total_vote_weight)

    # def is_valid(self):
    #     vote_time = dt.strptime(self.ts,'%Y-%m-%d %H:%M:%S.%f')
    #     start_time = dt.strptime(self.proposal.proposal_start_time,'%Y-%m-%d %H:%M:%S.%f')
    #     end_time = dt.strptime(self.proposal.proposal_end_time,'%Y-%m-%d %H:%M:%S.%f')
    #     if vote_time >= start_time: 
    #         if vote_time < end_time:
    #             return True
    #     return False
    
    def format_output(self):
        return {
            'proposal_title': self.proposal.proposal_title,
            'voter': self.voter.address,
            'known_as': self.voter.known_as,
            'choice': self.choice,
            'voting_weight': self.voting_weight,
            'total_weight': self.total_vote_weight,
            'choice_percent': self.choice_percent(),
            'available_power': self.available_power,
            'choice_power': self.choice_power(),
            'timestamp': self.ts,
            'proposal_start': self.proposal.proposal_start_time,
            'proposal_end': self.proposal.proposal_end_time,
            'period_end_date':  get_period_end_date(self.proposal.proposal_end_time),
            # 'period': get_period(),
            'valid': self.vote.is_valid(),
            'vote_id': self.vote_id,
        }


# ['cDAI+cUSDC (0xA2B4…)', 'cDAI+cUSDC+USDT (0x52EA…)', 'yDAI+yUSDC+yUSDT+yTUSD (0x45F7…)', 'yDAI+yUSDC+yUSDT+yBUSD (0x79a8…)', 'ycDAI+ycUSDC+ycUSDT+USDP (0x0636…)', 'renBTC+WBTC (0x9305…)', 'DAI+USDC+USDT+sUSD (0xA540…)', 'renBTC+WBTC+sBTC (0x7fC7…)', 'HBTC+WBTC (0x4CA9…)', 'DAI+USDC+USDT (0xbEbc…)', 'GUSD+3Crv (0x4f06…)', 'USDK+3Crv (0x3E01…)', 'USDN+3Crv (0x0f9c…)', 'mUSD+3Crv (0x8474…)', 'RSV+3Crv (0xC18c…)', 'DUSD+3Crv (0x8038…)', 'BBTC+sbtcCrv (0x071c…)', 'oBTC+sbtcCrv (0xd81d…)', 'pBTC+sbtcCrv (0x7F55…)', 'EURS+sEUR (0x0Ce6…)', 'ETH+sETH (0xc542…)', 'aDAI+aUSDC+aUSDT (0xDeBF…)', 'ETH+stETH (0xDC24…)', 'ETH+ankrETH (0xA96A…)', 'aDAI+aSUSD (0xEB16…)', 'iDAI+iUSDC+iUSDT (0x2dde…)', 'LINK+sLINK (0xF178…)', 'USDP+3Crv (0x42d7…)', 'TUSD+3Crv (0xEcd5…)', 'BUSD+3Crv (0x4807…)', 'FRAX+3Crv (0xd632…)', 'LUSD+3Crv (0xEd27…)', 'ETH+rETH (0xF944…)', 'alUSD+3Crv (0x43b4…)', 'USDT+WBTC+WETH (0xD51a…)', 'EURT+sEUR (0xFD5d…)', 'MIM+3Crv (0x5a6A…)', 'OUSD+3Crv (0x8765…)', 'CRV+cvxCRV (0x9D04…)', 'ibJPY+sJPY (0x8818…)', 'ibGBP+sGBP (0xD6Ac…)', 'ibAUD+sAUD (0x3F1B…)', 'ibEUR+sEUR (0x19b0…)', 'ibCHF+sCHF (0x9c2C…)', 'ibKRW+sKRW (0x8461…)', 'ETH+alETH (0xC4C3…)', 'EURN+EURT (0x3Fb7…)', 'USDP+3Crv (0xc270…)', 'wibBTC+sbtcCrv (0xFbdC…)', 'USDC+EURS (0x98a7…)', 'EURT+3Crv (0x9838…)', 'DOLA+3Crv (0xAA5A…)', 'tBTC+sbtcCrv (0xfa65…)', 'agEUR+EURT+EURS (0xb944…)', 'WETH+CRV (0x8301…)', 'RAI+3Crv (0x6187…)', 'WETH+CVX (0xB576…)', 'XAUt+3Crv (0xAdCF…)', 'WETH+T (0x752e…)', 'WETH+SPELL (0x9863…)', 'ibEUR+agEUR (0xB37D…)', 'BADGER+WBTC (0x50f3…)', 'ETH+FXS (0x941E…)', 'ETH+YFI (0xC26b…)', 'DYDX+ETH (0x8b0a…)', 'ETH+SDT (0xfB88…)', 'CADC+USDC (0xE07B…)', 'PWRD+3Crv (0xbcb9…)', 'FXS+cvxFXS (0xd658…)', 'rETH+wstETH (0x447D…)', 'pBTC+sbtcCrv (0xC946…)', 'Silo+FRAX (0x9a22…)', 'STG+USDC (0x3211…)', 'ETH+LFT (0xfE4A…)', 'sETH2+stETH (0xE95E…)', 'ibAUD+USDC (0x5b69…)', 'ibCHF+USDC (0x6Df0…)', 'ibEUR+USDC (0x1570…)', 'ibGBP+USDC (0xAcCe…)', 'ibJPY+USDC (0xEB02…)', 'ibKRW+USDC (0xef04…)', 'ETH+KP3R (0x2141…)', 'FRAX+FPI (0xf861…)', 'ETH+JPEG (0x7E05…)', 'PUSd+3Crv (0x8EE0…)', 'OHM+ETH (0x6ec3…)', 'FXS+sdFXS (0x8c52…)', 'ANGLE+sdANGLE (0x48fF…)', 'CRV+sdCRV (0xf7b5…)', 'USDC+USDT (0x1005…)', 'USDD+3Crv (0xe6b5…)', 'ETH+PAL (0x75A6…)', 'ETH+TOKE (0xe0e9…)', 'FRAX+USDC (0xDcEF…)', 'xFraxTempleLP+UNI-V2 (0xdaDf…)', 'EUROC+3Crv (0xE84f…)', 'sUSD+FRAXBP (0xe3c1…)', 'LUSD+FRAXBP (0x497C…)', 'ApeUSD+FRAXBP (0x04b7…)', 'GUSD+FRAXBP (0x4e43…)', 'BUSD+FRAXBP (0x8fdb…)', 'alUSD+FRAXBP (0xB30d…)', 'USDD+FRAXBP (0x4606…)', 'TUSD+FRAXBP (0x33ba…)', 'cEUR+agEUR+EUROC (0xe7A3…)', 'PUSd+FRAXBP (0xC47E…)', 'DOLA+FRAXBP (0xE571…)', 'agEUR+FRAXBP (0x5825…)', 'CVX+FRAXBP (0xBEc5…)', 'cvxCRV+FRAXBP (0x31c3…)', 'cvxFXS+FRAXBP (0x21d1…)', 'ALCX+FRAXBP (0x4149…)', 'agEUR+EUROC (0xBa34…)', 'MAI+FRAXBP (0x66E3…)', 'ETH+cbETH (0x5FAE…)', 'BADGER+FRAXBP (0x13B8…)', 'ETH+BTRFLY (0x6e31…)', 'CRV+yCRV (0x453D…)', 'RSR+FRAXBP (0x6a62…)', 'ETH+pETH (0x9848…)', 'ETH+frxETH (0xa1F8…)', 'JPEG+pETH (0x808d…)', 'XAI+FRAXBP (0x3262…)', 'SDT+FRAXBP (0x3e3C…)', 'cUSD+FRAXBP (0xA500…)', 'MIM+FRAXBP (0xb3bC…)', 'ftm-FRAX+DAI+USDC (0x7a65…)', 'ftm-miMATIC+fUSDT+USDC (0xA58F…)', 'ftm-MIM+fUSDT+USDC (0x2dd7…)', 'ftm-USDL Stablecoin+g3CRV (0x6EF7…)', 'ftm-FTM+Fantom-L (0x8B63…)', 'ftm-gDAI+gUSDC+gfUSDT (0x0fa9…)', 'ftm-DAI+USDC (0x27E6…)', 'ftm-BTC+renBTC (0x3eF6…)', 'ftm-fUSDT+BTC+ETH (0x3a16…)', 'poly-TUSD+am3CRV (0xAdf5…)', 'poly-EURS+am3CRV (0x9b3d…)', 'poly-amDAI+amUSDC+amUSDT (0x445F…)', 'poly-am3CRV+amWBTC+amWETH (0x9221…)', 'poly-amWBTC+renBTC (0xC2d9…)', 'poly-EURT+am3CRV (0xB446…)', 'poly-aMATICb+WMATIC (0x81c8…)', 'arbi-VST+FRAX (0x59bF…)', 'arbi-USDC+USDT (0x7f90…)', 'arbi-WBTC+renBTC (0x3E01…)', 'arbi-USDT+WBTC+WETH (0x960e…)', 'arbi-EURS+2CRV (0xA827…)', 'arbi-FRAX+USDC (0xC9B8…)', 'ava-AVAX+AVAX-L (0x4451…)', 'ava-avWBTC+renBTC (0x16a7…)', 'ava-avDAI+avUSDC+avUSDT (0x7f90…)', 'ava-av3CRV+avWBTC+avWETH (0xB755…)', 'op-sUSD+3CRV (0x061b…)', 'op-ETH+sETH (0x7Bc5…)', 'op-sBTC+WBTC (0x9F2f…)', 'op-DAI+USDC+USDT (0x1337…)', 'op-FRAX+USDC (0x29A3…)', 'xdai-WXDAI+USDC+USDT (0x7f90…)', 'VeFunder-vyper']
# ['NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', '1', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA']

# ['["cDAI+cUSDC (0xA2B4…)","cDAI+cUSDC+USDT (0x52EA…)","yDAI+yUSDC+yUSDT+yTUSD (0x45F7…)","yDAI+yUSDC+yUSDT+yBUSD (0x79a8…)","ycDAI+ycUSDC+ycUSDT+USDP (0x0636…)","DAI+USDC+USDT+sUSD (0xA540…)","HBTC+WBTC (0x4CA9…)","DAI+USDC+USDT (0xbEbc…)","GUSD+3Crv (0x4f06…)","USDK+3Crv (0x3E01…)","USDN+3Crv (0x0f9c…)","mUSD+3Crv (0x8474…)","RSV+3Crv (0xC18c…)","DUSD+3Crv (0x8038…)","EURS+sEUR (0x0Ce6…)","ETH+sETH (0xc542…)","aDAI+aUSDC+aUSDT (0xDeBF…)","ETH+stETH (0xDC24…)","ETH+ankrETH (0xA96A…)","aDAI+aSUSD (0xEB16…)","iDAI+iUSDC+iUSDT (0x2dde…)","LINK+sLINK (0xF178…)","USDP+3Crv (0x42d7…)","TUSD+3Crv (0xEcd5…)","BUSD+3Crv (0x4807…)","FRAX+3Crv (0xd632…)","LUSD+3Crv (0xEd27…)","ETH+rETH (0xF944…)","alUSD+3Crv (0x43b4…)","USDT+WBTC+WETH (0xD51a…)","EURT+sEUR (0xFD5d…)","MIM+3Crv (0x5a6A…)","OUSD+3Crv (0x8765…)","CRV+cvxCRV (0x9D04…)","ibJPY+sJPY (0x8818…)","ibGBP+sGBP (0xD6Ac…)","ibAUD+sAUD (0x3F1B…)","ibEUR+sEUR (0x19b0…)","ibCHF+sCHF (0x9c2C…)","ibKRW+sKRW (0x8461…)","ETH+alETH (0xC4C3…)","EURN+EURT (0x3Fb7…)","USDP+3Crv (0xc270…)","USDC+EURS (0x98a7…)","EURT+3Crv (0x9838…)","DOLA+3Crv (0xAA5A…)","agEUR+EURT+EURS (0xb944…)","WETH+CRV (0x8301…)","RAI+3Crv (0x6187…)","WETH+CVX (0xB576…)","XAUt+3Crv (0xAdCF…)","WETH+T (0x752e…)","WETH+SPELL (0x9863…)","ibEUR+agEUR (0xB37D…)","BADGER+WBTC (0x50f3…)","ETH+FXS (0x941E…)","ETH+YFI (0xC26b…)","DYDX+ETH (0x8b0a…)","ETH+SDT (0xfB88…)","CADC+USDC (0xE07B…)","PWRD+3Crv (0xbcb9…)","FXS+cvxFXS (0xd658…)","rETH+wstETH (0x447D…)","Silo+FRAX (0x9a22…)","STG+USDC (0x3211…)","ETH+LFT (0xfE4A…)","sETH2+stETH (0xE95E…)","ibAUD+USDC (0x5b69…)","ibCHF+USDC (0x6Df0…)","ibEUR+USDC (0x1570…)","ibGBP+USDC (0xAcCe…)","ibJPY+USDC (0xEB02…)","ibKRW+USDC (0xef04…)","ETH+KP3R (0x2141…)","FRAX+FPI (0xf861…)","ETH+JPEG (0x7E05…)","PUSd+3Crv (0x8EE0…)","OHM+ETH (0x6ec3…)","FXS+sdFXS (0x8c52…)","ANGLE+sdANGLE (0x48fF…)","CRV+sdCRV (0xf7b5…)","USDC+USDT (0x1005…)","USDD+3Crv (0xe6b5…)","ETH+PAL (0x75A6…)","ETH+TOKE (0xe0e9…)","FRAX+USDC (0xDcEF…)","xFraxTempleLP+UNI-V2 (0xdaDf…)","EUROC+3Crv (0xE84f…)","sUSD+FRAXBP (0xe3c1…)","LUSD+FRAXBP (0x497C…)","ApeUSD+FRAXBP (0x04b7…)","GUSD+FRAXBP (0x4e43…)","BUSD+FRAXBP (0x8fdb…)","alUSD+FRAXBP (0xB30d…)","USDD+FRAXBP (0x4606…)","TUSD+FRAXBP (0x33ba…)","cEUR+agEUR+EUROC (0xe7A3…)","PUSd+FRAXBP (0xC47E…)","DOLA+FRAXBP (0xE571…)","agEUR+FRAXBP (0x5825…)","CVX+FRAXBP (0xBEc5…)","cvxCRV+FRAXBP (0x31c3…)","cvxFXS+FRAXBP (0x21d1…)","ALCX+FRAXBP (0x4149…)","agEUR+EUROC (0xBa34…)","MAI+FRAXBP (0x66E3…)","ETH+cbETH (0x5FAE…)","BADGER+FRAXBP (0x13B8…)","ETH+BTRFLY (0x6e31…)","CRV+yCRV (0x453D…)","RSR+FRAXBP (0x6a62…)","ETH+pETH (0x9848…)","ETH+frxETH (0xa1F8…)","JPEG+pETH (0x808d…)","XAI+FRAXBP (0x3262…)","SDT+FRAXBP (0x3e3C…)","cUSD+FRAXBP (0xA500…)","MIM+FRAXBP (0xb3bC…)","bLUSD+LUSD3CRV-f (0x74ED…)","OHM+FRAXBP (0xFc1e…)","YFI+sdYFI (0x79E2…)","WBTC+sBTC (0xf253…)","pBTC+sbtc2Crv (0x141a…)","multiBTC+sbtc2Crv (0x2863…)","GEAR+ETH (0x0E9B…)","pitchFXS+FXS (0x0AD6…)","agEUR+EURe (0x4139…)","TRYB+3Crv (0x51Bc…)","CVX+clevCVX (0xF907…)","clevUSD+FRAXBP (0x84C3…)","ETH+CLEV (0x342D…)","ftm-FRAX+DAI+USDC (0x7a65…)","ftm-miMATIC+fUSDT+USDC (0xA58F…)","ftm-MIM+fUSDT+USDC (0x2dd7…)","ftm-USDL Stablecoin+g3CRV (0x6EF7…)","ftm-FTM+Fantom-L (0x8B63…)","ftm-gDAI+gUSDC+gfUSDT (0x0fa9…)","ftm-DAI+USDC (0x27E6…)","ftm-fUSDT+BTC+ETH (0x3a16…)","poly-TUSD+am3CRV (0xAdf5…)","poly-EURS+am3CRV (0x9b3d…)","poly-amDAI+amUSDC+amUSDT (0x445F…)","poly-am3CRV+amWBTC+amWETH (0x9221…)","poly-EURT+am3CRV (0xB446…)","poly-aMATICb+WMATIC (0x81c8…)","poly-CRV+crvUSDBTCETH (0xc7c9…)","poly-MATIC+crvUSDBTCETH (0x7BBc…)","arbi-VST+FRAX (0x59bF…)","arbi-USDC+USDT (0x7f90…)","arbi-USDT+WBTC+WETH (0x960e…)","arbi-EURS+2CRV (0xA827…)","arbi-FRAX+USDC (0xC9B8…)","ava-AVAX+AVAX-L (0x4451…)","ava-avDAI+avUSDC+avUSDT (0x7f90…)","ava-av3CRV+avWBTC+avWETH (0xB755…)","ava-aAvaDAI+aAvaUSDC+aAvaUSDT (0xD2Ac…)","op-sUSD+3CRV (0x061b…)","op-ETH+sETH (0x7Bc5…)","op-sBTC+WBTC (0x9F2f…)","op-DAI+USDC+USDT (0x1337…)","op-FRAX+USDC (0x29A3…)","xdai-WXDAI+USDC+USDT (0x7f90…)","VeFunder-vyper"]']
# ['{"94":100}']



def get_df_snapshot():
    try:
        filename = 'convex_snapshot_' + current_file_title
        snapshot_dict = read_json(filename, 'source')
        df_snapshot = pd.json_normalize(snapshot_dict)

    except:
        filename = 'convex_snapshot_' + fallback_file_title
        snapshot_dict = read_json(filename, 'source')        
        df_snapshot = pd.json_normalize(snapshot_dict)
    return df_snapshot.sort_values("VOTE_TIMESTAMP", axis = 0, ascending = True)

def get_snapshot_obj(df_snapshot):
    snapshot = Snapshot()
    snapshot.process(df_snapshot)
    return snapshot

def get_df_vote_choice(snapshot):
    vote_choice_data = snapshot.format_final_choice_output()
    df_vote_choice = pd.json_normalize(vote_choice_data)
    return df_vote_choice.sort_values("proposal_start", axis = 0, ascending = True)


def get_aggregates(df_vote_choice):
    # dfs = []
    # titles = []
    # for title in df_vote_choice.proposal_title.unique():
    #     df_temp = df_vote_choice[
    #         df_vote_choice.proposal_title.isin([title])
    #     ]
    #     dfs.append(df_temp)
    #     titles.append(title)

    df_vote_aggregates = df_vote_choice.groupby(
        ['proposal_end', 'proposal_title', 'choice']
        )['choice_power'].agg(['sum','count']).reset_index()
    
    df_vote_aggregates = df_vote_aggregates.rename(columns={
        "sum": 'total_vote_power',
        'count': 'vlcvx_voter_count'})
    df_vote_aggregates =df_vote_aggregates.sort_values(["proposal_end", 'total_vote_power'], axis = 0, ascending = False)

    # dfs.append(df_vote_aggregates)
    # titles.append('Aggregates')
    return df_vote_aggregates



df_snapshot = get_df_snapshot()
snapshot = get_snapshot_obj(df_snapshot)
df_vote_choice = get_df_vote_choice(snapshot)
df_vote_aggregates = get_aggregates(df_vote_choice)





