from flask import current_app as app
from app.data.reference import filename_curve_liquidity, filename_curve_liquidity_aggregate

from datetime import datetime as dt
from datetime import datetime, timedelta
from app.utilities.utility import timed
import traceback


from app.data.local_storage import (
    pd,
    read_json, 
    read_csv,  
    write_dataframe_csv,
    write_dfs_to_xlsx
    )
from app.utilities.utility import get_period

try:
    gauge_registry = app.config['gauge_registry']
    df_all_by_gauge = app.config['df_all_by_gauge']

except:
    from app.curve.gauges.models import gauge_registry
    from app.curve.gauge_rounds.models import df_all_by_gauge

class LiquidityProcessor():
    def __init__(self, _df_liquidity):
        self.gauge_registry = gauge_registry
        self.df_all_by_gauge = df_all_by_gauge
        self.df_liquidity = _df_liquidity
        self.output = []
        self.all_by_gauge_address = {}
        self.period_filtered_by_gauge = {}
        self.last_output_per_gauge_per_asset = {}
        self.total_records = {}
        self.process_liquidity()

    def process_liquidity(self):
        self.output = []
        for index, row in self.df_liquidity.iterrows():
            # if index % 1000 == 0:
                # print(f"index: {index}")
            # Process Row
            is_success = self.process_row(row)
            # Some Rows fail to find a gauge. If so skip to next row
            if not is_success:
                # print("not successful")
                continue
            # Need to determine if gaps in data. 
            # And if so, fill them
            gauge_addr = self.output[-1]['gauge_addr']
            token_symbol = self.output[-1]['token_symbol']
            this_output = self.output[-1]

            # Most spam only has one balance change. 
            ##  To fight filling in spam transactions, 
            ##  Track how many records there are per gauge/token
            if not gauge_addr in self.total_records:
                self.total_records[gauge_addr] = {}
                self.total_records[gauge_addr][token_symbol] = 0
            elif not token_symbol in self.total_records[gauge_addr]:
                self.total_records[gauge_addr][token_symbol] = 0
            self.total_records[gauge_addr][token_symbol] += 1
            
            # If first record then start here and skip filling in missing data
            if (
                gauge_addr in self.last_output_per_gauge_per_asset and
                token_symbol in self.last_output_per_gauge_per_asset[gauge_addr]
                ):
                last_output = self.last_output_per_gauge_per_asset[gauge_addr][token_symbol]
            else:
                last_output = None
            # Loop to fill in missing dates between records
            while self.is_there_a_gap(this_output, last_output):
                last_output = last_output.copy()
                date = last_output['date']
                date_next = date +  timedelta(days=1)
                last_output['date'] = date_next
                last_output['delta_native'] = 0
                last_output['delta_usd'] = 0
                self.process_row(last_output, False)
            if not gauge_addr in self.last_output_per_gauge_per_asset:
                self.last_output_per_gauge_per_asset[gauge_addr] = {}
            self.last_output_per_gauge_per_asset[gauge_addr][token_symbol] = this_output
        # Loop to fill in missing between last and today
        # print("MADE IT TO FILLING IN FINAL GAPS")
        # print(f"~Today: {now}")
        self.fill_in_gaps_to_current_date()

    def is_there_a_gap(self, this_output, last_output, this_output_is_date=False):
        # If Return True, next record procssed is 1 day later than last_ouput
        # As such there is always a minimum of 1 day buffer in when True is returned
        if last_output:
            if this_output_is_date:
                # Current record does not exist (so process one more time to create current days record)
                date_spread = this_output - last_output['date']
                # print(f"Date Now {this_output}\tDate Compare {last_output['date']}")
                # print(f"Date spread {date_spread}")
                if date_spread.days >= 1:
                    # print("\n\tProcess next day\n")
                    return True
            else:
                # Current record exists
                date_spread = this_output['date'] - last_output['date']
                if date_spread.days > 1:
                    # print(f"\tfill in: {last_output['date']} to {this_output['date']} | Days to go: {date_spread.days - 1}")
                    # print(f"\t\t{last_output['display_symbol']} | {last_output['token_symbol']}")
                    return True
        return False
    

    def fill_in_gaps_to_current_date(self):
        # Loop to fill in missing between last and today
        # print("MADE IT TO FILLING IN FINAL GAPS")
        now = dt.now().date()
        # print(f"~Today: {now}")
        for gauge_key in self.last_output_per_gauge_per_asset.keys():
            record = self.last_output_per_gauge_per_asset[gauge_key]
            for asset_key in record.keys():
                # Filter out records where there was only one balance update to fight spam tokens
                if self.total_records[gauge_key][asset_key] < 2:
                    # print(f"\tSkipping Token: {asset_key}")
                    continue
                # print(f"Gauge: \n\t{gauge_key} \n Asset \n\t{asset_key}")
                last_output = record[asset_key]
                # print(last_output)
                while self.is_there_a_gap(now, last_output, True):
                    last_output = last_output.copy()
                    date = last_output['date']
                    date_next = date +  timedelta(days=1)
                    last_output['date'] = date_next
                    last_output['delta_native'] = 0
                    last_output['delta_usd'] = 0        
                    self.process_row(last_output, False)


    def process_row(self, row, is_row_raw= True):
        if is_row_raw:
            date = row['date'] if 'date' in row else row['DATE']
            date = dt.strptime(date[:10],'%Y-%m-%d')
            date = date.date()
            token_address = row['contract_address'] if 'contract_address' in row else row['CONTRACT_ADDRESS']
            token_name = row['token_name'] if 'token_name' in row else row['TOKEN_NAME']
            pool_address = row['user_address'] if 'user_address' in row else row['USER_ADDRESS']
            token_symbol = row['symbol'] if 'symbol' in row else row['SYMBOL']
            has_price = row['has_price'] if 'has_price' in row else row['HAS_PRICE']
            # bal_delta = row['bal_delta'] if 'bal_delta' in row else row['BAL_DELTA']
            # bal_delta_usd = row['bal_delta_usd'] if 'bal_delta_usd' in row else row['BAL_DELTA_USD']
            current_bal = row['current_bal'] if 'current_bal' in row else row['CURRENT_BAL']
            current_bal_usd = row['current_bal_usd'] if 'current_bal_usd' in row else row['CURRENT_BAL_USD']
            current_bal = float(current_bal)
            current_bal_usd = float(current_bal_usd)
            has_price = False if has_price == 'False' or has_price == 'false' else True
        else:
            date = row['date']
            token_address = row['token_address']
            token_name = row['token_name']
            token_symbol = row['token_symbol']

            pool_address = row['pool_address']
            has_price = row['has_price']
            # bal_delta = row['native_delta']
            # bal_delta_usd = row['usd_delta']
            current_bal = row['liquidity_native']
            current_bal_usd = row['liquidity'] 
            # print(f"\t\tFilling {date}")    

        try:
            # Try to match pool with a gauge address
            if pool_address in self.gauge_registry.pools:
                gauge_addr = self.gauge_registry.pools[pool_address].gauge_addr
                pool_name = self.gauge_registry.pools[pool_address].pool_name
                pool_symbol = self.gauge_registry.pools[pool_address].pool_symbol
                if not pool_symbol:
                    if self.gauge_registry.pools[pool_address].token_symbol:
                        pool_symbol = self.gauge_registry.pools[pool_address].pool_symbol


            else: 
                # print("Couldn't find in gauge_registry")
                return False
        
            # Minimize filter by gauge address
            # all_by_gauge_address[gauge_addr] = gauge votes filtered by that gauge address
            if not gauge_addr in self.all_by_gauge_address:
                df_all_by_gauge_search = self.df_all_by_gauge[
                    self.df_all_by_gauge.gauge_addr.isin([gauge_addr])
                ]
                self.all_by_gauge_address[gauge_addr] = df_all_by_gauge_search

            df_all_by_gauge_search = self.all_by_gauge_address[gauge_addr]

            # Minimize Filter by Date
            ##  Store last date search          
            ##  period_filtered_by_gauge[gauge_addr] = gauge votes 
            ##    filtered by that gauge address before this date     
            if not gauge_addr in self.period_filtered_by_gauge:
                temp_df_1 = df_all_by_gauge_search[df_all_by_gauge_search.period_end_date <= date]
                self.period_filtered_by_gauge[gauge_addr] = temp_df_1      

            ## Get difference between Date and last Period End Date
            period_filtered_this_gauge = self.period_filtered_by_gauge[gauge_addr]
            if len(period_filtered_this_gauge) == 0:
                date_spread = 0
            else:
                date_spread = date - period_filtered_this_gauge.iloc[0]['period_end_date'] 
                date_spread = date_spread.days    
            ## If more than a week, update vote information to more recent. 
            if is_row_raw:
                temp_df_3 = df_all_by_gauge_search[df_all_by_gauge_search.period_end_date < date]
                temp_df_3.sort_values(['period_end_date'], axis = 0, ascending = False)

            elif date_spread > 7 or len(period_filtered_this_gauge) == 0:
                temp_df_2 = df_all_by_gauge_search[df_all_by_gauge_search.period_end_date < date]
                temp_df_2.sort_values(['period_end_date'], axis = 0, ascending = False)
                self.period_filtered_by_gauge[gauge_addr] = temp_df_2

                temp_df_3 = self.period_filtered_by_gauge[gauge_addr] 
            else:
                temp_df_3 = self.period_filtered_by_gauge[gauge_addr] 


            # ## Filter shitty vote percent
            try:
                vote_percent = temp_df_3.iloc[0]['vote_percent']
                total_vote_power = temp_df_3.iloc[0]['total_vote_power']
            #     if vote_percent < 0.0001:
            #         liquidity_vs_percent = 0
            #         liquidity_vs_votes = 0
            #     else:
            #         liquidity_vs_percent = current_bal_usd / vote_percent
            #         liquidity_vs_votes = current_bal_usd / temp_df_3.iloc[0]['total_vote_power']
            except Exception as e:
                vote_percent = 0      
                total_vote_power = 0
            self.output.append({
                # from this source
                'date': date,
                'pool_address': pool_address,
                'pool_name': pool_name,
                'pool_symbol': pool_symbol,
                'gauge_addr': gauge_addr,
                'liquidity_native': current_bal,
                'liquidity': current_bal_usd,

                # new vs prior version
                'has_price': has_price,
                # 'native_delta': bal_delta,
                # 'usd_delta': bal_delta_usd,
                'token_name': token_name,
                'token_address': token_address,
                'token_symbol': token_symbol,

                # derrived from others

                'total_votes': total_vote_power,
                # 'symbol': temp_df_3.iloc[0]['symbol'],
                'percent': vote_percent,
                # 'liquidty_vs_percent': liquidity_vs_percent,
                # 'liquidty_vs_votes': liquidity_vs_votes,

                # 'tradeable_assets': tradeable_assets,
                'display_name': f"{pool_name} ({pool_address[0:6]})",
                'display_symbol': f"{pool_symbol} ({pool_address[0:6]})"
                })
            
        except Exception as e:
            print(f"Could not process pool {pool_name} \n\t {pool_address}")
            print(e)
            print(traceback.format_exc())
            return False 
        return True
    
    # WIP
    ## Sometimes removes pools if only single deposit and no further action
    ## But tradeoff feels reasonable to purge spam
    def purge_shitcoins(self, df):
        for gauge_key in self.total_records:
            for asset_key in self.total_records[gauge_key]:
                if self.total_records[gauge_key][asset_key] < 2:
                    # print(f"Removing {asset_key} from {gauge_key}")
                    df = df[~(
                            (df['token_symbol'] == asset_key) & 
                            (df['gauge_addr'] == gauge_key)
                        )]
        return df
            
    def get_df(self):
        out_df = self.purge_shitcoins(pd.json_normalize(self.output))
        try:
            out_df = out_df.sort_values(['date', 'liquidity'], axis = 0, ascending = False)
        except:
            pass
        return out_df 
    

def get_df_gauge_votes():
    filename = filename_curve_liquidity    #+ fallback_file_title
    resp_dict = read_csv(filename, 'raw_data')
    df_gauge_votes = pd.json_normalize(resp_dict)
    try:
        df_gauge_votes = df_gauge_votes.sort_values("date", axis = 0, ascending = True)
    except:
        df_gauge_votes = df_gauge_votes.sort_values("DATE", axis = 0, ascending = True)
    return df_gauge_votes

def get_aggregates(df):
    df_curve_liquidity_aggregates = df.groupby([
            'date',
            'pool_address',
            'pool_name',
            'pool_symbol',
            'gauge_addr',
            'display_name',
            'display_symbol'
        ]).agg(
        liquidity_native=pd.NamedAgg(column='liquidity_native', aggfunc=sum),
        liquidity=pd.NamedAgg(column='liquidity', aggfunc=sum),
        # native_delta=pd.NamedAgg(column='native_delta', aggfunc=sum),

        # usd_delta=pd.NamedAgg(column='usd_delta', aggfunc=sum),
        total_votes=pd.NamedAgg(column='total_votes', aggfunc=max),
        percent=pd.NamedAgg(column='percent', aggfunc=max),
        token_symbol=pd.NamedAgg(column='token_symbol', aggfunc=list),
        has_price=pd.NamedAgg(column='has_price', aggfunc=list),

    ).reset_index()

    df_curve_liquidity_aggregates['liquidity_over_votes'] = (
        df_curve_liquidity_aggregates['liquidity'].divide(df_curve_liquidity_aggregates['total_votes'])
    )

    df_curve_liquidity_aggregates['liquidity_native_over_votes'] = (
        df_curve_liquidity_aggregates['liquidity_native'].divide(df_curve_liquidity_aggregates['total_votes'])
    )
    df_curve_liquidity_aggregates.sort_values("date", axis = 0, ascending = False )
    return df_curve_liquidity_aggregates

def process_and_save():
    print("Processing... { curve.liquidity.models }")
    lp = LiquidityProcessor(get_df_gauge_votes())
    df_curve_liquidity = lp.get_df()
    df_curve_liquidity_aggregates = get_aggregates(df_curve_liquidity)
    write_dataframe_csv(filename_curve_liquidity, df_curve_liquidity, 'processed')

    write_dataframe_csv(filename_curve_liquidity_aggregate, df_curve_liquidity_aggregates, 'processed')
    try:
        # app.config['df_active_votes'] = df_active_votes
        app.config['df_curve_liquidity'] = df_curve_liquidity
        app.config['df_curve_liquidity_aggregates'] = df_curve_liquidity_aggregates
    except:
        print("could not register in app.config\n\tGauge Votes")
    return {
        # 'df_active_votes': df_active_votes,
        'df_curve_liquidity': df_curve_liquidity,
        'df_curve_liquidity_aggregates': df_curve_liquidity_aggregates,
    }


    # all_votes, active_votes = vr.format_active_output()
    # # df_active_votes = pd.json_normalize(active_votes)
    # df_all_votes = pd.json_normalize(all_votes)
    # write_dataframe_csv(filename_curve_gauge_votes_all, df_all_votes, 'processed')

    # df_gauge_votes_formatted = get_votes_formatted(vr)
    # write_dataframe_csv(filename_curve_gauge_votes_formatted, df_gauge_votes_formatted, 'processed')

    # df_current_gauge_votes = get_current_votes(df_gauge_votes_formatted)
    # write_dataframe_csv(filename_curve_gauge_votes_current, df_current_gauge_votes, 'processed')

    # try:
    #     # app.config['df_active_votes'] = df_active_votes
    #     app.config['df_all_votes'] = df_all_votes
    #     app.config['df_gauge_votes_formatted'] = df_gauge_votes_formatted
    #     app.config['df_current_gauge_votes'] = df_current_gauge_votes
    # except:
    #     print("could not register in app.config\n\tGauge Votes")
    # return {
    #     # 'df_active_votes': df_active_votes,
    #     'df_all_votes': df_all_votes,
    #     'df_gauge_votes_formatted': df_gauge_votes_formatted,
    #     'df_current_gauge_votes': df_current_gauge_votes
    # }


