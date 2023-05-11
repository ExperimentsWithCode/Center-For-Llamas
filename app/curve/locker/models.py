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
    current_file_title,
    fallback_file_title
)


class Govenor():
    def __init__(self, address):
        self.address = address
        self.actions = {}
        self.actions_list = []
        self.supply_list = []
        self.deposit_list = []
        self.withdraw_list = []
        self.final_balance = 0
        self.final_lock_time = 0
        self.final_supply = 0
        self.history = []
        if self.address in known_large_curve_holders:
            self.known_as = known_large_curve_holders[self.address]
        else:
            self.known_as = "_"
        
    def add_action(self, row):
        event_name = row['EVENT_NAME']
        if row['DECODED_LOG'] == None:
            print("No Action!")
            return
        log = ast.literal_eval(row['DECODED_LOG'])
        if event_name == 'Deposit':
            action = Deposit(row, log)
            self.deposit_list.append(action)
            self.final_balance += int(action.value)
            self.final_lock_time = action.locktime
        elif event_name == 'Supply':
            action = Supply(row, log)
            self.supply_list.append(action)
            self.final_supply = int(action.supply)
        elif event_name == 'Withdraw':
            action = Withdraw(row, log)
            self.withdraw_list.append(action)
            self.final_balance -= int(action.value)

        else:
            print("No Action")
            # print(row)
            return
        self.actions[row['TX_HASH']] = action
        self.actions_list.append(action)
        if not event_name == 'Supply': 
            self.history.append({
                'address': self.address,
                'known_as': self.known_as,
                'provider': action.provider,
                'balance': self.final_balance,
                'balance_adj': self.final_balance * (10** -18),
                'final_lock_time': dt.fromtimestamp(self.final_lock_time),
                'timestamp': action.block_timestamp,
                'period': get_period(action.week_num, action.week_day, action.block_timestamp),
                'period_end_date': get_period_end_date(action.block_timestamp),
                'balance_adj_formatted': "{:,.2f}".format(self.final_balance * (10** -18))
            })


    def format_output(self):
        output_data = {'supply': self.format_output_supply(),
                       'deposit': self.format_output_deposit(),
                        'withdraw': self.format_output_withdraw() }
        # print (output_data)
        return output_data
 
    
    def format_output_deposit(self):
        output_data = []

        for deposit in self.deposit_list:
            output_data.append(deposit.format_output())
        # print(output_data)
        return output_data
    
    def format_output_withdraw(self):
        output_data = []
        for withdraw in self.withdraw_list:
            output_data.append(withdraw.format_output())
        # print(output_data)
        return output_data
    
    def format_output_supply(self):
        output_data = []
        for supply in self.supply_list:
            output_data.append(supply.format_output())
        # print(output_data)
        return output_data

class Deposit():
    def __init__(self, row, log):
        self.block_number = row['BLOCK_NUMBER']
        self.block_timestamp = row['BLOCK_TIMESTAMP']
        self.address = row['ORIGIN_FROM_ADDRESS']

        self.locktime = log['locktime']
        self.provider = log['provider']
        self.ts = log['ts']
        self.type = log['type']
        self.value = log['value']
        self.week_num = int(row['WEEK_NUMBER'])
        self.week_day = int(row['WEEK_DAY'])

    def format_output(self):
        return {
            'block_number': self.block_number,
            'block_timestamp': self.block_timestamp,
            'address': self.address,
            # 'known_as': self.known_as,

            'locktime': self.locktime,
            'provider': self.provider,
            'ts': self.ts,
            'type': self.type,
            'value': self.value,
            'balance_adj': int(self.value) * (10** -18),
            'period': get_period(self.week_num, self.week_day, self.block_timestamp),
        }

class Supply():
    def __init__(self, row, log):
        self.block_number = row['BLOCK_NUMBER']
        self.block_timestamp = row['BLOCK_TIMESTAMP']
        self.address = row['ORIGIN_FROM_ADDRESS']
        self.previous_supply = log['prevSupply']
        self.supply =log['supply']
        self.week_num = int(row['WEEK_NUMBER'])
        self.week_day = int(row['WEEK_DAY'])

    def format_output(self):
        return {
            'block_number': self.block_number,
            'block_timestamp': self.block_timestamp,
            'address': self.address,
            'previous_supply': self.previous_supply,
            'supply': self.supply,
            'period': get_period(self.week_num, self.week_day, self.block_timestamp),
        }

            
class Withdraw():
    def __init__(self, row, log):
        self.block_number = row['BLOCK_NUMBER']
        self.block_timestamp = row['BLOCK_TIMESTAMP']
        self.address = row['ORIGIN_FROM_ADDRESS']
        self.provider = log['provider']
        self.ts = log['ts']
        self.value = log['value']
        self.week_num = int(row['WEEK_NUMBER'])
        self.week_day = int(row['WEEK_DAY'])

    def format_output(self):
        return {
            'block_number': self.block_number,
            'block_timestamp': self.block_timestamp,
            'address': self.address,
            'provider': self.provider,
            'ts': self.ts,
            'value': self.value,
            'balance_adj': int(self.value) * (10** -18),
            'period': get_period(self.week_num, self.week_day, self.block_timestamp),
        }


class Locker():
    def __init__(self):
        self.govenors = {}
        
    def new_govenor(self, row):
        address = row['ORIGIN_FROM_ADDRESS']
        if not row['DECODED_LOG'] == None:
            log = ast.literal_eval(row['DECODED_LOG'])
            if 'provider' in log:
                address = log['provider']
        if not address in self.govenors:
            g = Govenor(address)
            self.govenors[address] = g
        return self.govenors[address]

    def process_locks(self, df):
        for index, row in df.iterrows():
            g = self.new_govenor(row)
            if g:
                a = g.add_action(row)
            else:
                print("")
        
    def format_output(self):
        output_data = {'supply': [],
                        'deposit': [],
                        'withdraw': [],
                        }
        for k in self.govenors:
            # print(k)
            g = self.govenors[k]
            g_out =  g.format_output()
            # print(g_out)
            # print(output_data)

            output_data['supply'] += g_out['supply']
            output_data['withdraw'] += g_out['withdraw']
            output_data['deposit'] += g_out['deposit']
        return output_data

    def format_history_output(self):
        output_data = []
        for k in self.govenors:
            g = self.govenors[k]
            output_data += g.history
        return output_data



def get_df_locker():
    try:
        filename = 'curve_locker_through_'+ current_file_title
        locker_dict = read_csv(filename, 'source')
        df_locker = pd.json_normalize(locker_dict)

    except:
        filename = 'curve_locker_through_'+ fallback_file_title
        locker_dict = read_csv(filename, 'source')    
        df_locker = pd.json_normalize(locker_dict)
    df_locker = df_locker.sort_values("BLOCK_TIMESTAMP", axis = 0, ascending = True)
    return df_locker


def get_locker_obj():
    locker = Locker()
    locker.process_locks(df_locker)
    return locker

def get_history(locker):
    history_data = locker.format_history_output()
    df_history_data = pd.json_normalize(history_data)
    df_history_data = df_history_data.sort_values("timestamp", axis = 0, ascending = True)
    return df_history_data   


def get_current_locks(df_history_data):
    now = dt.now()
    df_current_locks = df_history_data.groupby('provider', as_index=False).last()
    df_current_locks = df_current_locks[df_current_locks['balance_adj'] > 2]
    df_current_locks = df_current_locks[df_current_locks['final_lock_time'] > now]
    df_current_locks = df_current_locks.sort_values("balance_adj", axis = 0, ascending = False)
    return df_current_locks


df_locker = get_df_locker()
locker = get_locker_obj()

x = locker.format_output()
df_locker_supply = pd.json_normalize(x['supply'])
df_locker_withdraw = pd.json_normalize(x['withdraw'])
df_locker_deposit = pd.json_normalize(x['deposit'])


df_history_data  = get_history(locker)


df_current_locks = get_current_locks(df_history_data)

df_known_locks = df_current_locks.groupby(['known_as']).sum('balance_adj').reset_index()

app.config['df_locker_supply'] = df_locker_supply
app.config['df_locker_withdraw'] = df_locker_withdraw
app.config['df_locker_deposit'] = df_locker_deposit

app.config['df_history_data'] = df_history_data
app.config['df_current_locks'] = df_current_locks

app.config['df_known_locks'] = df_known_locks



