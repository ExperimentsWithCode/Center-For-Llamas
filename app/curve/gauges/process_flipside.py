from flask import current_app as app
from app import MODELS_FOLDER_PATH, RAW_FOLDER_PATH
from app.data.reference import filename_curve_gauges

import math
# import numpy as np 

from app.data.local_storage import (
    pd,
    read_json,
    read_csv,
    df_to_csv,
    write_dfs_to_xlsx,
    csv_to_df,
    df_to_csv
    )

# filename = 'crv_locker_logs'

    
from datetime import datetime as dt

from app.utilities.utility import (
    get_checkpoint_id, 
    get_checkpoint_timestamp_from_id, 
    convert_units,
    print_mode
    )
from app.data.reference import (
    known_large_market_actors,
    current_file_title,
    fallback_file_title
)

from app.data.source.harvested_core_pools import core_pools
from app.data.source.chain_ids import chain_id_map


class GaugeRegistry():
    def __init__(self, df, core_pools=core_pools):
        self.gauges = {}
        self.pools = {}
        self.tokens = {}
        self.shorthand_gauges = {}
        self.shorthand_pools = {}
        self.shorthand_tokens = {}

        self.process_list(core_pools)
        self.process_df(df)
        self.process_curve_api()

    def process_df(self, df):
        for i, row in df.iterrows():
            self.process_row(row)

    def process_list(self, core_pools):
        for row in core_pools:
            self.process_row(row)

    def process_curve_api(self):
        data = read_json('get_all_gauges', 'source')
        d = data['data']
        df_gauges = pd.DataFrame.from_dict(d, orient='index')
        for i, row in df_gauges.iterrows():
            self.process_curve_info(row)

    def nan_helper(self, value):
        if type(value) == float:
            return math.isnan(value) 
        return not bool(value)
    
    def process_curve_info(self, row):
        new_row = {}
        new_row['is_pool'] = row['isPool']
        # new_row[''] = row['poolUrls']
        new_row['pool_addr'] = None if self.nan_helper(row['swap']) else row['swap']
        new_row['token_addr'] = None if self.nan_helper(row['swap_token']) else row['swap_token']
        new_row['gauge_name'] = None if self.nan_helper(row['name']) else row['name']


        new_row['gauge_addr'] = None if self.nan_helper(row['gauge']) else row['gauge']
        # Unique Data
        new_row['display_name'] = None if self.nan_helper(row['shortName']) else row['shortName']
        new_row['gauge_crv_apy'] = None if self.nan_helper(row['gaugeCrvApy']) else row['gaugeCrvApy']
        new_row['gauge_crv_future_apy'] = None if self.nan_helper(row['gaugeFutureCrvApy']) else row['gaugeFutureCrvApy']
        new_row['is_factory'] = None if self.nan_helper(row['factory']) else row['factory']
        new_row['is_sidechain'] = None if self.nan_helper(row['side_chain']) else row['side_chain']
        new_row['is_killed'] = None if self.nan_helper(row['is_killed']) else row['is_killed']
        new_row['crv_type'] = None if self.nan_helper(row['type']) else row['type']
        new_row['lending_vault_addr'] = None if self.nan_helper(row['lendingVaultAddress']) else row['lendingVaultAddress']
        new_row['vote_timestamp'] = None
        new_row['deployed_timestamp'] = None
        new_row['type_id'] = ''
        new_row['type_name'] = ''
        new_row['name'] = ''
        new_row['symbol'] = ''
        new_row['weight'] = ''
        new_row['type_weight'] = ''
        new_row['type_total_weight'] = ''
        new_row['type_weight_time'] = ''
        new_row['tx_hash'] = ''
        new_row['chain_id'] = ''
        
        self.process_row(new_row)


    def process_row(self, row):
        if 'gauge_addr' in row:
            gauge_addr = row['gauge_addr']
        elif 'GAUGE_ADDR' in row:
            gauge_addr = row['GAUGE_ADDR']
        else:
            gauge_addr = "XX"
        if gauge_addr in self.gauges:
            gs_old = self.gauges[gauge_addr]
        else:
            gs_old = None
        gs = Gauge_Set(row, gs_old)
        if gs.gauge_addr:
            self.gauges[gs.gauge_addr.lower()] = gs
            self.shorthand_gauges[gs.gauge_addr[:6].lower()] = gs
            
        if gs.pool_addr and gs.pool_addr:
            self.pools[gs.pool_addr.lower()] = gs
            self.shorthand_pools[gs.pool_addr[:6].lower()] = gs

        if gs.token_addr:
            self.tokens[gs.token_addr.lower()] = gs
            self.shorthand_tokens[gs.token_addr[:6].lower()] = gs

    def get_value(self, gauge_addr, key):
        if gauge_addr in self.gauges:
            this_gauge = self.gauges[gauge_addr].format_output()
            if key in this_gauge:
                return this_gauge[key]
        return None
    
    def format_output(self):
        output_data = []
        for gauge in self.gauges:
            gauge_set = self.gauges[gauge]
            output_data.append(gauge_set.format_output())
        return output_data

    def get_gauge(self, address):
        address = address.lower()
        if address in self.gauges:
            return self.gauges[address]
        else:
            return None

    def get_gauge_name(self, address):
        address = address.lower()
        if address in self.gauges:
            return self.gauges[address].gauge_name
        else:
            return None

    def get_gauge_symbol(self, address):
        address = address.lower()
        if address in self.gauges:
            return self.gauges[address].gauge_symbol
        else:
            return None

    def get_gauge_set_from_snapshot(self, gauge_reference):
        if len(gauge_reference) > 8:
            x = gauge_reference.find('(')
            y = gauge_reference.find(')') +1
            partial_addr = gauge_reference[x:y][1:7].lower()

            # partial_addr = gauge_reference[-8:-2].lower()
        else:
            partial_addr = gauge_reference
        if partial_addr in self.shorthand_pools:
            return self.shorthand_pools[partial_addr]
        elif partial_addr in self.shorthand_tokens:
            return self.shorthand_tokens[partial_addr]
        elif partial_addr in self.shorthand_gauges:
            return self.shorthand_gauges[partial_addr]
        return None

    def get_gauge_address_from_snapshot(self, gauge_reference):
        gauge_set = self.get_gauge_set_from_snapshot(gauge_reference)
        if gauge_set:
            return gauge_set.gauge_addr
        return None

    def get_gauge_display_name(self, gauge_addr):
        if gauge_addr in self.gauges:
            ga = self.gauges[gauge_addr]

            partial_addr = ga.gauge_addr[0:6].lower()
            return f"{ga.gauge_symbol} ({partial_addr})"


        return None
    
    def get_shorthand_pool(self, gauge_addr):
        if gauge_addr in self.shorthand_pools:
            return self.shorthand_pools[gauge_addr]
        else:
            return None
        
    def get_gauge_addr_from_pool(self, pool_addr):
        if pool_addr in self.pools:
            return self.pools[pool_addr].gauge_addr
    
    def get_gauge_name_from_pool(self, pool_addr):
        if pool_addr in self.pools:
            return self.pools[pool_addr].gauge_name

    def get_gauge_symbol_from_pool(self, pool_addr):
        if pool_addr in self.pools:
            return self.pools[pool_addr].gauge_symbol

    def get_gauge_source_from_pool(self, pool_addr):
        if pool_addr in self.pools:
            return self.pools[pool_addr].source
    


class Gauge_Set():
    def __init__(self, row, prior_record=None):
        try:
            split = row['deployed_timestamp'].split("T")
            row['deployed_timestamp'] = split[0]+" "+split[1][:-1]
            # row['block_timestamp'] = dt.strptime(row['block_timestamp'], '%Y-%m-%d %H:%M:%S.%f'),
        except:
            pass
        try:
            split = row['vote_timestamp'].split("T")
            row['vote_timestamp'] = split[0]+" "+split[1][:-1]
            # row['block_timestamp'] = dt.strptime(row['block_timestamp'], '%Y-%m-%d %H:%M:%S.%f'),
        except:
            pass
        # print(row.keys())
        self.display_name = None
        self.gauge_crv_apy = None # Added by process curve api
        self.gauge_crv_future_apy = None # Added by process curve api
        self.is_factory = None # Added by process curve api
        self.is_sidechain = None # Added by process curve api
        self.is_killed = None # Added by process curve api
        self.crv_type = None # Added by process curve api
        self.lending_vault_addr = None # Added by process curve api

        self.gauge_addr = row['gauge_addr']
        self.gauge_name = row['gauge_name'] if 'gauge_name' in row else None
        self.gauge_symbol = row['gauge_symbol'] if 'gauge_symbol' in row else None

        self.pool_addr = row['pool_addr'] if 'pool_addr' in row else None
        self.pool_name = row['pool_name'] if 'pool_name' in row else None
        self.pool_symbol = row['pool_symbol'] if 'pool_symbol' in row else None

        if self.pool_addr and len(self.pool_addr) > 0:
            self.pool_partial = self.pool_addr[:6]
        else:
            self.pool_partial = None
        self.token_addr = row['token_addr'] if 'token_addr' in row else None
        self.token_name = row['token_name'] if 'token_name' in row else None
        self.token_symbol = row['token_symbol'] if 'token_symbol' in row else None

        self.source = row['source'] if 'source' in row else ''

        self.deployed_timestamp = row['deployed_timestamp'] if 'deployed_timestamp' in row else None
        self.vote_timestamp = row['vote_timestamp'] if 'vote_timestamp' in row else None
        
        if not self.deployed_timestamp:
            self.deployed_timestamp = None
        if not self.vote_timestamp:
            self.vote_timestamp = None
        # For deployments
        try:
            self.deployed_period = get_checkpoint_id(row['deployed_timestamp'])
            self.deployed_period_end_date = get_checkpoint_timestamp_from_id(self.deployed_period)
        except Exception as e:
            self.deployed_period = None   
            self.deployed_period_end_date = None

        # For Approvals
        try:
            self.first_period = get_checkpoint_id(row['vote_timestamp'])
            self.first_period_end_date = get_checkpoint_timestamp_from_id(self.first_period)
        except Exception as e:
            self.first_period = None   
            self.first_period_end_date = None

        try:
            self.type_id                = row['type_id']
            self.type_name              = row['type_name']
            self.name                   = row['name']
            self.symbol                 = row['symbol']
            self.weight                 = row['weight']
            self.type_weight            = row['type_weight']
            self.type_total_weight      = row['type_total_weight']
            self.type_weight_time       = row['type_weight_time']
            self.tx_hash                = row['tx_hash']
            self.chain_id               = int(row['chain_id']) if bool(row['chain_id']) else ''
            self.chain_name             = None

        except:
            self.type_id                = None
            self.type_name              = None
            self.name                   = None
            self.symbol                 = None
            self.weight                 = None
            self.type_weight            = None
            self.type_total_weight      = None
            self.type_weight_time       = None
            self.tx_hash                = None
            self.chain_id               = None
            self.chain_name             = None

        if self.chain_id:
            try:
                self.chain_id = int(self.chain_id)
                self.chain_name = chain_id_map[self.chain_id]
            except:
                pass

        self.type_weight_adj = convert_units(self.type_weight)
        self.type_total_weight_adj = convert_units(self.type_total_weight, 18+26)

        if not self.gauge_name:
            if self.name:
                self.gauge_name = self.name
        if not self.gauge_symbol:
            if self.symbol:
                self.gauge_symbol = self.symbol

        self.process_curve_api(row)
        self.process_old(prior_record)
        self.process_names()

    def process_names(self):
        # Pass names up stack if available
        if not self.gauge_name and self.pool_name:
            self.gauge_name = self.pool_name
        if not self.gauge_symbol and self.pool_symbol:
            self.gauge_symbol = self.pool_symbol
        if not self.gauge_name and self.display_name:
            self.gauge_name = self.display_name
        if not self.gauge_symbol and self.display_name:
            self.gauge_symbol = self.display_name

    def process_old(self, prior_record):
        if prior_record:
            if not self.gauge_name and prior_record.gauge_name:
                self.gauge_name = prior_record.gauge_name

            if not self.gauge_symbol and prior_record.gauge_symbol:
                self.gauge_symbol = prior_record.gauge_symbol

            # Pool
            if not self.pool_addr and prior_record.pool_addr:
                self.pool_addr = prior_record.pool_addr
                self.pool_partial = self.pool_addr[:6]

            if not self.pool_name and prior_record.pool_name:
                self.pool_name = prior_record.pool_name

            if not self.pool_symbol and prior_record.pool_symbol:
                self.pool_symbol = prior_record.pool_symbol
            # Token
            if not self.token_addr and prior_record.token_addr:
                self.token_addr = prior_record.token_addr

            if not self.token_name and prior_record.token_name:
                self.token_name = prior_record.token_name

            if not self.token_symbol and prior_record.token_symbol:
                self.token_symbol = prior_record.token_symbol
#
            if not self.type_id and prior_record.type_id:
                self.type_id = prior_record.type_id

            if not self.type_name and prior_record.type_name:
                self.type_name = prior_record.type_name
            # Token
            if not self.name and prior_record.name:
                self.name = prior_record.name

            if not self.symbol and prior_record.symbol:
                self.symbol = prior_record.symbol

            if not self.type_weight and prior_record.type_weight:
                self.type_weight = prior_record.type_weight
                self.type_weight_adj = prior_record.type_weight_adj

            if not self.type_total_weight and prior_record.type_total_weight:
                self.type_total_weight = prior_record.type_total_weight
                self.type_total_weight_adj = prior_record.type_total_weight_adj

            if not self.type_weight_time and prior_record.type_weight_time:
                self.type_weight_time = prior_record.type_weight_time

            if not self.tx_hash and prior_record.tx_hash:
                self.tx_hash = prior_record.tx_hash
            # Token
            if not self.vote_timestamp and prior_record.vote_timestamp:
                self.vote_timestamp = prior_record.vote_timestamp

            if prior_record.chain_id and prior_record.chain_id > 1:
                self.chain_id = prior_record.chain_id

            if not self.chain_name and prior_record.chain_name:
                self.chain_name = prior_record.chain_name

            if not self.first_period and prior_record.first_period:
                self.first_period = prior_record.first_period

            if not self.first_period_end_date and prior_record.first_period_end_date:
                self.first_period_end_date = prior_record.first_period_end_date

            if not self.deployed_period and prior_record.deployed_period:
                self.deployed_period = prior_record.deployed_period

            if not self.deployed_period_end_date and prior_record.deployed_period_end_date:
                self.deployed_period_end_date = prior_record.deployed_period_end_date

            if not self.deployed_timestamp and prior_record.deployed_timestamp:
                self.deployed_timestamp = prior_record.deployed_timestamp

            if len(self.source) == 0 and len(prior_record.source) > 0:
                self.source = prior_record.source


    def process_curve_api(self, row):
        if 'gauge_crv_apy' in row:
            self.display_name = row['display_name']
            self.gauge_crv_apy = row['gauge_crv_apy']
            self.gauge_crv_future_apy = row['gauge_crv_future_apy']
            self.is_factory = row['is_factory']
            self.is_sidechain = row['is_sidechain']
            self.is_killed = row['is_killed']
            self.crv_type = row['crv_type']
            self.lending_vault_addr = row['lending_vault_addr']
        return None


    def format_output(self):
        return {
            'gauge_addr'        : self.gauge_addr,
            'gauge_name'        : self.gauge_name,
            'gauge_symbol'      : self.gauge_symbol,
            'pool_addr'         : self.pool_addr,
            'pool_name'         : self.pool_name,
            'pool_symbol'       : self.pool_symbol,
            'pool_partial'      : self.pool_partial,
            'token_addr'        : self.token_addr,
            'token_name'        : self.token_name,
            'token_symbol'      : self.token_symbol,
            'source'            : self.source,
            'deployed_timestamp' : self.deployed_timestamp,
            'first_period'      : self.first_period,
            'first_period_end_date': self.first_period_end_date,
            'deployed_period'   : self.deployed_period,
            'deployed_period_end_date' : self.deployed_period_end_date,

            'type_id'           : self.type_id,
            'type_name'         : self.type_name,
            'name'              : self.name,
            'symbol'            : self.symbol,
            'weight'            : self.weight,
            'type_weight'       : self.type_weight,
            'type_weight_adj'   : self.type_weight_adj,
            'type_total_weight' : self.type_total_weight,
            'type_total_weight_adj' : self.type_total_weight_adj,

            'type_weight_time'  : self.type_weight_time,
            'tx_hash'           : self.tx_hash,
            'vote_timestamp'    : self.vote_timestamp,
            'chain_id'          : self.chain_id,
            'chain_name'        : self.chain_name,

            'display_name'      : self.display_name,
            'gauge_crv_apy'     : self.gauge_crv_apy,
            'gauge_crv_future_apy' : self.gauge_crv_future_apy,
            'is_factory'        : self.is_factory,
            'is_sidechain'      : self.is_sidechain,
            'is_killed'         : self.is_killed,
            'crv_type'          : self.crv_type,
            'lending_vault_addr' : self.lending_vault_addr,
        }


def get_df_gauge_pool_map():
    filename = filename_curve_gauges    # _'+ current_file_title
    df_gauge_pool_map = csv_to_df(filename, RAW_FOLDER_PATH)

    # df_gauge_pool_map = df_gauge_pool_map.sort_values("BLOCK_TIMESTAMP", axis = 0, ascending = True)
    return df_gauge_pool_map

def process_and_save():
    print_mode("Processing... { curve.gauges.models }")

    gauge_registry = GaugeRegistry(get_df_gauge_pool_map(), core_pools)
    df = pd.json_normalize(gauge_registry.format_output())
    df_to_csv(df, filename_curve_gauges, MODELS_FOLDER_PATH)

    return df

def process_and_get():
    print_mode("Processing... { curve.gauges.models }")
    gauge_registry = GaugeRegistry(get_df_gauge_pool_map(), core_pools)
    return gauge_registry


# ,type_id,
# type_name,
# name,
# symbol,
# gauge_addr,
# weight,
# type_weight,
# type_total_weight,
# type_weight_time,
# tx_hash,
# vote_timestamp,
# pool_addr,
# token_addr,
# source,
# deployed_timestamp,
# gauge_name,
# gauge_symbol,
# pool_name
# ,pool_symbol
# ,token_name
# ,token_symbol
# ,__row_index
