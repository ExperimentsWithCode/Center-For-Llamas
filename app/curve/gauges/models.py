from flask import current_app as app
from app import MODELS_FOLDER_PATH

from app.data.reference import filename_curve_gauges

from app.data.local_storage import (
    pd,
    read_json,
    read_csv,
    write_dataframe_csv,
    write_dfs_to_xlsx,
    csv_to_df
    )
# from app.curve.gauges.process_flipside import process_and_get, process_and_save

from app.utilities.utility import nullify_amount, print_mode

 
print_mode("Loading... { curve.gauges.models }")


class GaugeRegistryModel():
    def __init__(self, df):
        self.df_root = df
        self.gauges = {}
        self.pools = {}
        self.tokens = {}
        self.shorthand_gauges = {}
        self.shorthand_pools = {}
        self.shorthand_tokens = {}
        self.process()
        
    def process(self):
        for i, row in self.df_root.iterrows():
            gs = GaugeSetModel(row)
            if gs.gauge_addr:
                self.gauges[gs.gauge_addr] = gs
                self.shorthand_gauges[gs.gauge_addr[:6]] = gs
                
            if gs.pool_addr and gs.pool_addr:
                self.pools[gs.pool_addr] = gs
                self.shorthand_pools[gs.pool_addr[:6]] = gs

            if gs.token_addr:
                self.tokens[gs.token_addr] = gs
                self.shorthand_tokens[gs.token_addr[:6]] = gs

    def get_value(self, gauge_addr, key):
        if gauge_addr in self.gauges:
            this_gauge = self.gauges[gauge_addr].format_output()
            if key in this_gauge:
                return this_gauge[key]
        return None
    
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

class GaugeSetModel():
    def __init__(self, row):
        self.row = row
        self.gauge_addr = row['gauge_addr'] 
        self.gauge_name = row['gauge_name'] 
        self.gauge_symbol = row['gauge_symbol'] 
        self.pool_addr = row['pool_addr'] 
        self.pool_name = row['pool_name']
        self.pool_symbol = row['pool_symbol'] 
        self.pool_partial = row['pool_partial'] 
        self.token_addr = row['token_addr'] 
        self.token_name = row['token_name']
        self.token_symbol = row['token_symbol'] 
        self.source = row['source'] 
        self.deployed_timestamp = row['deployed_timestamp'] 
        self.first_period = row['first_period']
        self.first_period_end_date = row['first_period_end_date'] 
        self.deployed_period = row['deployed_period'] 
        self.deployed_period_end_date = row['deployed_period_end_date']
        self.type_id = row['type_id'] 
        self.type_name = row['type_name'] 
        self.name = row['name'] 
        self.symbol = row['symbol'] 
        self.weight = row['weight'] 
        self.type_weight = row['type_weight']
        self.type_weight_adj = row['type_weight_adj'] 
        self.type_total_weight = row['type_total_weight'] 
        self.type_total_weight_adj = row['type_total_weight_adj']
        self.type_weight_time = row['type_weight_time'] 
        self.tx_hash = row['tx_hash'] 
        self.vote_timestamp = row['vote_timestamp'] 
        self.chain_id = row['chain_id']
        self.chain_name = row['chain_name'] 
        self.display_name = row['display_name'] 
        self.gauge_crv_apy = row['gauge_crv_apy'] 
        self.gauge_crv_future_apy = row['gauge_crv_future_apy']
        self.is_factory = row['is_factory'] 
        self.is_sidechain = row['is_sidechain'] 
        self.is_killed = row['is_killed'] 
        self.crv_type = row['crv_type']
        self.lending_vault_addr = row['lending_vault_addr']
        
        

def format_df(df):
    # df['gauge_addr']            = df['gauge_addr'].astype(str)
    # df['gauge_name']            = df['gauge_name'].astype(str)
    # df['gauge_symbol']          = df['gauge_symbol'].astype(str)
    # df['pool_addr']             = df['pool_addr'].astype(str)
    # df['pool_name']             = df['pool_name'].astype(str)
    # df['pool_symbol']           = df['pool_symbol'].astype(str)
    # df['pool_partial']          = df['pool_partial'].astype(str)
    # df['token_addr']            = df['token_addr'].astype(str)
    # df['token_name']            = df['token_name'].astype(str)
    # df['token_symbol']          = df['token_symbol'].astype(str)
    # df['source']                = df['source'].astype(str)
    df['deployed_timestamp']    = pd.to_datetime(df['deployed_timestamp'])
    # if 'first_period' in df.keys():
    #     df['first_period']          = df['first_period'].astype(int)
    #     df['deployed_period']          = df['deployed_period'].astype(int)

    df['first_period_end_date'] = pd.to_datetime(df['first_period_end_date']).dt.date
    df['deployed_period_end_date'] = pd.to_datetime(df['deployed_period_end_date']).dt.date

    if 'type_id' in df.keys():
        df['type_id'] = df.apply(
            lambda x: nullify_amount(x['type_id']), 
            axis=1)
        
    # df['type_name']             = df['type_name'].astype(str)
    # df['name']                  = df['name'].astype(str)
    # df['symbol']                = df['symbol'].astype(str)
    if 'weight' in df.keys():
        df['weight'] = df.apply(
            lambda x: nullify_amount(x['weight']), 
            axis=1)
    # df['type_weight']           = df['type_weight'].astype(float)
    # df['type_total_weight']     = df['type_total_weight'].astype(int)
    # df['type_weight_time']      = df['type_weight_time'].astype(int)
    # df['tx_hash']               = df['tx_hash'].astype(str)
    df['vote_timestamp'] = pd.to_datetime(df['vote_timestamp'])
    # df['chain_id']              = df['chain_id'].astype(int)
    # df['chain_name']            = df['chain_name'].astype(str)
    return df


def get_gauge_registry(is_already_borked=False):
    try:
        filename = filename_curve_gauges    # _'+ current_file_title
        df = csv_to_df(filename, MODELS_FOLDER_PATH)
        df = format_df(df)
    except:
        try:
            filename = filename_curve_gauges    # '+ fallback_file_title
            gauge_pool_map = read_json(filename, MODELS_FOLDER_PATH)
            df = pd.json_normalize(gauge_pool_map)
            df = format_df(df)
        except:
            # return process_and_save()
            pass
    return df

df_curve_gauge_registry = get_gauge_registry()
gauge_registry = GaugeRegistryModel(df_curve_gauge_registry)

try:
    app.config['df_curve_gauge_registry'] = df_curve_gauge_registry
    app.config['gauge_registry'] = gauge_registry
except:
    print_mode("could not register in app.config\n\tGauges")


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
