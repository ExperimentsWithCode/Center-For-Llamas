from flask import current_app as app
from app.data.reference import filename_curve_gauges

from app.data.local_storage import (
    pd,
    read_json,
    read_csv,
    write_dataframe_csv,
    write_dfs_to_xlsx,
    csv_to_df,
    write_dataframe_csv
    )

# filename = 'crv_locker_logs'

from datetime import datetime as dt

from app.utilities.utility import get_checkpoint_id, get_checkpoint_timestamp_from_id, convert_units
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


    def process_df(self, df):
        for i, row in df.iterrows():
            self.process_row(row)

    def process_list(self, core_pools):
        for row in core_pools:
            self.process_row(row)

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
        if gs.pool_addr:
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
        try:
            self.gauge_addr = row['GAUGE_ADDR']
            self.gauge_name = row['GAUGE_NAME']
            self.gauge_symbol = row['GAUGE_SYMBOL']

            self.pool_addr = row['POOL_ADDR']
            self.pool_name = row['POOL_NAME']
            self.pool_symbol = row['POOL_SYMBOL']
            if self.pool_addr:
                self.pool_partial = self.pool_addr[:6]
            else:
                self.pool_partial = None
            self.token_addr = row['TOKEN_ADDR']
            self.token_name = row['TOKEN_NAME']
            self.token_symbol = row['TOKEN_SYMBOL']

            self.source = row['SOURCE']

            # self.deployed_timestamp = row['BLOCK_TIMESTAMP'] if 'BLOCK_TIMESTAMP' in row else None
        except:
            # print(row.keys())
            self.gauge_addr = row['gauge_addr']
            self.gauge_name = row['gauge_name']
            self.gauge_symbol = row['gauge_symbol']

            self.pool_addr = row['pool_addr']
            self.pool_name = row['pool_name']
            self.pool_symbol = row['pool_symbol']
            if self.pool_addr:
                self.pool_partial = self.pool_addr[:6]
            else:
                self.pool_partial = None
            self.token_addr = row['token_addr']
            self.token_name = row['token_name']
            self.token_symbol = row['token_symbol']

            self.source = row['source']

            self.deployed_timestamp = row['deployed_timestamp'] if 'deployed_timestamp' in row else None

        try:
            self.deployed_period = get_checkpoint_id(row['deployed_timestamp'])
            self.deployed_period_end_date = get_checkpoint_timestamp_from_id(self.deployed_period)
        except Exception as e:
            self.deployed_period = None   
            self.deployed_period_end_date = None

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
            self.vote_timestamp         = row['vote_timestamp']
            self.chain_id               = row['chain_id']
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
            self.vote_timestamp         = None
            self.chain_id               = None
            self.chain_name             = None

        self.type_weight_adj = convert_units(self.type_weight)
        self.type_total_weight_adj = convert_units(self.type_total_weight, 18+26)

        if self.chain_id:
            try:
                self.chain_id = int(self.chain_id)
                self.chain_name = chain_id_map[self.chain_id]
            except:
                pass

        if not self.gauge_name:
            if self.name:
                self.gauge_name = self.name
        if not self.gauge_symbol:
            if self.symbol:
                self.gauge_symbol = self.symbol
        self.process_old(prior_record)

    def process_old(self, prior_record):
        if prior_record:
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

    def format_output(self):
        return {
            'gauge_addr' : self.gauge_addr,
            'gauge_name' : self.gauge_name,
            'gauge_symbol' : self.gauge_symbol,
            'pool_addr' : self.pool_addr,
            'pool_name' : self.pool_name,
            'pool_symbol' : self.pool_symbol,
            'pool_partial': self.pool_partial,
            'token_addr' : self.token_addr,
            'token_name' : self.token_name,
            'token_symbol' : self.token_symbol,
            'source' : self.source,
            'deployed_timestamp' : self.deployed_timestamp,
            'first_period': self.first_period,
            'first_period_end_date': self.first_period_end_date,
            'deployed_period' : self.deployed_period,
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
            'chain_name'        : self.chain_name

        }


def get_df_gauge_pool_map():
    filename = filename_curve_gauges    # _'+ current_file_title
    df_gauge_pool_map = csv_to_df(filename, 'raw_data')

    # df_gauge_pool_map = df_gauge_pool_map.sort_values("BLOCK_TIMESTAMP", axis = 0, ascending = True)
    return df_gauge_pool_map

def process_and_save():
    print("Processing... { curve.gauges.models }")

    gauge_registry = GaugeRegistry(get_df_gauge_pool_map(), core_pools)
    df = pd.json_normalize(gauge_registry.format_output())
    write_dataframe_csv(filename_curve_gauges, df, 'processed')
    try:
        app.config['df_curve_gauge_registry'] = df
        app.config['gauge_registry'] = gauge_registry
    except:
        print("could not register in app.config\n\tGauges")
    return df

def process_and_get():
    print("Processing... { curve.gauges.models }")
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
