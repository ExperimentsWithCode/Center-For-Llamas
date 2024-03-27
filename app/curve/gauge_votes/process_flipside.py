from flask import current_app as app
from app.data.reference import (
    filename_curve_gauge_votes,
    filename_curve_gauge_votes_all,
    filename_curve_gauge_votes_formatted,
    filename_curve_gauge_votes_current
)

# from ... import db
# from app.utilities.utility import timed

from app.data.local_storage import (
    pd,
    read_json,
    read_csv,
    write_dataframe_csv,
    write_dfs_to_xlsx
    )

import ast
from datetime import datetime as dt

from app.utilities.utility import (
    get_period, 
    get_period_end_date, 
    get_checkpoint_timestamp, 
    get_checkpoint_id
)

from app.data.reference import (
    known_large_curve_holders,
    gauge_names,
    gauge_symbols,
    current_file_title,
    fallback_file_title,
)
from flask import current_app as app

try:
    # curve_gauge_registry = app.config['df_curve_gauge_registry']
    gauge_registry = app.config['gauge_registry']
except: 
    # from app.curve.gauges import df_curve_gauge_registry as curve_gauge_registry
    from app.curve.gauges.models import gauge_registry



class Voter():
    def __init__(self, address):
        self.address = address
        self.votes = []
        self.active_votes = {}
        self.known_as = "_"
        if self.address in known_large_curve_holders:
            self.known_as = known_large_curve_holders[self.address]

    def new_vote(self, row):
        if 'TX_HASH' in row:
            tx_hash = row['TX_HASH']
            try:
                decoded_log = ast.literal_eval(row['DECODED_LOG'])
                gauge_addr = decoded_log['gauge_addr']
                time = dt.fromtimestamp(decoded_log['time'])
                user = decoded_log['user']
                weight = decoded_log['weight']
                temp_name = gauge_registry.get_gauge_name(gauge_addr)
                if temp_name:
                    name = temp_name
                elif  gauge_addr in gauge_names:
                    name = gauge_names[gauge_addr]
                elif 'NAME' in row:
                    name = row['NAME']
                    if name == 'null':
                        name = ""
                else:
                    name = ""
                if 'SYMBOL' in row:
                    symbol = row['SYMBOL']
                    if symbol == 'null':
                        if gauge_addr in gauge_symbols:
                            symbol = gauge_symbols[gauge_addr]
                        else:
                            temp_symbol = gauge_registry.get_gauge_symbol(gauge_addr)
                            symbol = temp_symbol if temp_symbol else ""

                elif gauge_addr in gauge_symbols:
                    symbol = gauge_symbols[gauge_addr]
                else:
                    symbol = ""
                if 'WEEK_NUMBER' in row:
                    week_num = int(row['WEEK_NUMBER'])
                    week_day = int(row['WEEK_DAY'])
                else:
                    week_num = -1
                    week_day = -1

                v = Vote(self, gauge_addr, time, user, weight, name, symbol, week_num, week_day)
                self.votes.append(v)
                self.active_votes[gauge_addr] = v
            except Exception as e:
                print(e)
                print(row['DECODED_LOG'])
        else:
            tx_hash = row['tx_hash']
            try:
                # decoded_log = ast.literal_eval(row['DECODED_LOG'])
                gauge_addr = row['decoded_log.gauge_addr']
                time = dt.fromtimestamp(int(row['decoded_log.time']))
                user = row['decoded_log.user']
                weight = int(row['decoded_log.weight'])
                temp_name = gauge_registry.get_gauge_name(gauge_addr)
                if temp_name:
                    name = temp_name
                elif  gauge_addr in gauge_names:
                    name = gauge_names[gauge_addr]
                elif 'name' in row:
                    name = row['name']
                    if name == 'null':
                        name = ""
                else:
                    name = ""
                    name = ""
                if 'symbol' in row:
                    symbol = row['symbol']
                    if symbol == 'null' or symbol == '':
                        if gauge_addr in gauge_symbols:
                            symbol = gauge_symbols[gauge_addr]
                        else:
                            temp_symbol = gauge_registry.get_gauge_symbol(gauge_addr)
                            symbol = temp_symbol if temp_symbol else ""

                elif gauge_addr in gauge_symbols:
                    symbol = gauge_symbols[gauge_addr]
                else:
                    symbol = ""
                if 'week_number' in row:
                    week_num = int(row['week_number'])
                    week_day = int(row['week_day'])
                else:
                    week_num = -1
                    week_day = -1

                v = Vote(self, gauge_addr, time, user, weight, name, symbol, week_num, week_day)
                self.votes.append(v)
                self.active_votes[gauge_addr] = v
            except Exception as e:
                # print(e)
                pass
                # print(row.keys())

    def active_format_output(self):
        output_data = []
        sum_weight = 0
        for k in self.active_votes:
            vote = self.active_votes[k]
            output_data.append(vote.format_output())
            sum_weight += vote.weight
        weight_data = {
            'known_as': self.known_as,
            'voter': self.address,
            'sum_weight': sum_weight, }
        return output_data, weight_data

    def format_output(self):
        output_data = []
        for vote in self.votes:
            # vote = self.votes[k]
            output_data.append(vote.format_output())
        return output_data



    # def format_output(self):






class Vote():
    def __init__(self, voter, gauge_addr, time, user, weight, name, symbol, week_num, week_day):
        self.voter = voter
        self.gauge_addr = gauge_addr
        self.time = time
        self.user = user
        self.weight = weight
        self.name = name
        self.symbol = symbol
        self.week_num = week_num
        self.week_day = week_day

    # def get_period(self):
    #     if self.week_num > -1 and self.week_day > -1:
    #         # vote_time = dt.strptime(self.time,'%Y-%m-%d %H:%M:%S.%f')
    #         vote_year = self.time.year
    #         if self.time.month == 1 and self.week_num == 52:
    #             self.week_num = 0
    #         if self.week_day > 5:
    #             week_num = self.week_num + 1
    #         else:
    #             week_num = self.week_num
    #         if week_num < 10 or week_num == 0:
    #             week_num = f"0{week_num}"
    #         return float(f"{vote_year}.{week_num}")
    #     print('WEEK NOT FOUND')
    #     print(self.week_day)
    #     print(self.week_num)
    #     return 0

    def format_output(self):
        return {
            "known_as": self.voter.known_as,
            "voter": self.voter.address,
            "gauge_addr": self.gauge_addr,
            "user": self.user,
            "time": self.time,
            "weight": self.weight,
            "name": self.name,
            "symbol": self.symbol,
            "period": get_period(self.week_num, self.week_day, self.time),
            "period_end_date": get_period_end_date(self.time),
            "checkpoint_id": get_checkpoint_id(self.time),
            "checkpoint_timestamp": get_checkpoint_timestamp(self.time)
        }


class VoterRegistry():
    def __init__(self):
        self.voters = {}


    def format_active_output(self):
        output_data = []
        out_weight_data = []
        for voter in self.voters:
            voter_data, weight_data = self.voters[voter].active_format_output()
            output_data += voter_data
            out_weight_data.append(weight_data)
        return output_data, out_weight_data


    def format_output(self):
        output_data = []
        for voter in self.voters:
            voter_data = self.voters[voter].format_output()
            output_data += voter_data
        return output_data


    def process(self, df):

        for index, row in df.iterrows():
            if 'VOTE_ADDR' in row:
                voter_address = row['VOTE_ADDR']
            else:
                voter_address = row['decoded_log.user']
            if not voter_address in self.voters:
                self.voters[voter_address] = Voter(voter_address)
            voter = self.voters[voter_address]

            voter.new_vote(row)



# @timed
def get_df_gauge_votes():
    try:
        filename = filename_curve_gauge_votes    #+ current_file_title
        resp_dict = read_csv(filename, 'raw_data')
        df_gauge_votes = pd.json_normalize(resp_dict)
        df_gauge_votes = df_gauge_votes.sort_values("BLOCK_TIMESTAMP", axis = 0, ascending = True)

    except:
        filename = filename_curve_gauge_votes    #+ fallback_file_title
        resp_dict = read_csv(filename, 'raw_data')
        df_gauge_votes = pd.json_normalize(resp_dict)
        df_gauge_votes = df_gauge_votes.sort_values("block_timestamp", axis = 0, ascending = True)

    return df_gauge_votes

# @timed
def get_vote_registry_obj():
    vr = VoterRegistry()
    vr.process(get_df_gauge_votes())
    return vr

# @timed
def get_votes_formatted(vr):
    vote_data = vr.format_output()
    df_gauge_votes_formatted = pd.json_normalize(vote_data)
    df_gauge_votes_formatted = df_gauge_votes_formatted.sort_values("time", axis = 0, ascending = True)
    return df_gauge_votes_formatted

# @timed
def get_current_votes(df_gauge_votes_formatted):
    df_current_gauge_votes = df_gauge_votes_formatted.groupby(['voter', 'gauge_addr'], as_index=False).last()
    df_current_gauge_votes = df_current_gauge_votes[df_current_gauge_votes['weight'] > 0]
    df_current_gauge_votes = df_current_gauge_votes.sort_values("time", axis = 0, ascending = False)
    return df_current_gauge_votes

def process_and_save():
    print("Processing... { curve.gauge_votes.models }")
    vr = get_vote_registry_obj()


    all_votes, active_votes = vr.format_active_output()
    # df_active_votes = pd.json_normalize(active_votes)
    df_all_votes = pd.json_normalize(all_votes)
    write_dataframe_csv(filename_curve_gauge_votes_all, df_all_votes, 'processed')

    df_gauge_votes_formatted = get_votes_formatted(vr)
    write_dataframe_csv(filename_curve_gauge_votes_formatted, df_gauge_votes_formatted, 'processed')

    df_current_gauge_votes = get_current_votes(df_gauge_votes_formatted)
    write_dataframe_csv(filename_curve_gauge_votes_current, df_current_gauge_votes, 'processed')

    try:
        # app.config['df_active_votes'] = df_active_votes
        app.config['df_all_votes'] = df_all_votes
        app.config['df_gauge_votes_formatted'] = df_gauge_votes_formatted
        app.config['df_current_gauge_votes'] = df_current_gauge_votes
    except:
        print("could not register in app.config\n\tGauge Votes")
    return {
        # 'df_active_votes': df_active_votes,
        'df_all_votes': df_all_votes,
        'df_gauge_votes_formatted': df_gauge_votes_formatted,
        'df_current_gauge_votes': df_current_gauge_votes
    }

