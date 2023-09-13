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

from app.utilities.utility import get_period, get_period_end_date
from app.data.reference import (
    known_large_curve_holders,
    current_file_title,
    fallback_file_title
)

from app.data.source.harvested_core_pools import core_pools





class GaugeRegistry():
    def __init__(self, df, core_pools=core_pools):
        self.gauges = {}
        self.pools = {}
        self.tokens = {}
        self.shorthand_gauges = {}
        self.shorthand_pools = {}
        self.shorthand_tokens = {}

        self.process_df(df)
        self.process_list(core_pools)


    def process_df(self, df):
        for i, row in df.iterrows():
            self.process_row(row)

    def process_list(self, core_pools):
        for row in core_pools:
            self.process_row(row)

    def process_row(self, row):
        gs = Gauge_Set(row)
        if gs.gauge_addr:
            self.gauges[gs.gauge_addr.lower()] = gs
            self.shorthand_gauges[gs.gauge_addr[:6].lower()] = gs
        if gs.pool_addr:
            self.pools[gs.pool_addr.lower()] = gs
            self.shorthand_pools[gs.pool_addr[:6].lower()] = gs
        if gs.token_addr:
            self.tokens[gs.token_addr.lower()] = gs
            self.shorthand_tokens[gs.token_addr[:6].lower()] = gs


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

    def get_gauge_name(self, gauge_reference):
        if len(gauge_reference) > 8:
            partial_addr = gauge_reference[-8:-2].lower()
            if partial_addr in self.shorthand_pools:
                return self.shorthand_pools[partial_addr]

        return None
    
    def get_shorthand_pool(self, gauge_addr):
        if gauge_addr in self.shorthand_pools:
            return self.shorthand_pools[gauge_addr]
        else:
            return None

class Gauge_Set():
    def __init__(self, row):
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

            self.type = row['TYPE']

            self.time_gauge_registered = row['BLOCK_TIMESTAMP'] if 'BLOCK_TIMESTAMP' in row else None
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

            self.type = row['type']

            self.time_gauge_registered = row['block_timestamp'] if 'block_timestamp' in row else None


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
            'type' : self.type,
            'time_gauge_registered' : self.time_gauge_registered,
        }


def get_df_gauge_pool_map():
    try:
        filename = 'gauge_to_lp_map'# _'+ current_file_title
        gauge_pool_map = read_csv(filename, 'source')
        df_gauge_pool_map = pd.json_normalize(gauge_pool_map)

    except:
        filename = 'gauge_to_lp_map'# '+ fallback_file_title
        gauge_pool_map = read_csv(filename, 'source')
        df_gauge_pool_map = pd.json_normalize(gauge_pool_map)
    # df_gauge_pool_map = df_gauge_pool_map.sort_values("BLOCK_TIMESTAMP", axis = 0, ascending = True)
    return df_gauge_pool_map

gauge_registry = GaugeRegistry(get_df_gauge_pool_map(), core_pools)
df_curve_gauge_registry = pd.json_normalize(gauge_registry.format_output())

try:
    app.config['df_curve_gauge_registry'] = df_curve_gauge_registry
    app.config['gauge_registry'] = gauge_registry
except:
    print("could not register in app.config\n\tGauges")
