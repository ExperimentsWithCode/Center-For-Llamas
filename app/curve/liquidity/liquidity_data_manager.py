from datetime import timedelta

from app.curve.liquidity.fetch import generate_query, fetch
from app.curve.liquidity.fetch_cutoff import fetch_cutoff
# from app.curve.liquidity.process_flipside import process_and_save
from app.data.flipside_api_helper import query_and_save


from app.data.local_storage import (
    pd,
    read_json,
    read_csv,
    write_dataframe_csv,
    write_dfs_to_xlsx,
    csv_to_df,
    df_to_csv,
    )
from app.utilities.utility import (
    get_datetime_obj
    )
from app.data.reference import (
    filename_curve_liquidity, 
    filename_curve_liquidity_cutoff
    )




def get_df_from_file(filename):
    resp_dict = read_csv(filename, 'raw_data')
    df = pd.json_normalize(resp_dict)
    return df

class LiquidityManager():
    def __init__(self,
                 should_fetch = True,
                 load_initial = False,
                 load_cutoff = False,
                 cutoff_value = None,
                 human_management = False,
                 ):
        self.load_initial = load_initial
        self.should_fetch = should_fetch
        self.load_cutoff = load_cutoff
        self.cutoff_value = cutoff_value
        self.human_management = human_management


    def manage(self):
        df_cutoff = self.cutoff()   # if load cutoff, load, else get
        self.backfill(df_cutoff)    # if load initial, load
        df_liquidity = self.forward_filler() # Each fetc doesn't see cutoff data and so wont return cutoff data
        df_joined = self.join_cutoff(df_liquidity, df_cutoff) # join before saving to source so processng uses both
        df_to_csv(df_joined, filename_curve_liquidity, 'source')


    def cutoff(self):
        """
        Cutoff
            Used as a backstop. 
            Derriving balance from transfers means 
            anything older than my oldest search fucks up balances
            so cutoff just aggregates sums prior to the cutoff  
        """
        if self.load_cutoff:
            if self.load_initial:
                if self.cutoff_value:
                    df_cutoff = fetch_cutoff(self.cutoff_value)
                else:
                    df_cutoff = fetch_cutoff()
                df_to_csv(df_cutoff, filename_curve_liquidity_cutoff, 'raw_data') 
        return get_df_from_file(filename_curve_liquidity_cutoff)

    def backfill(self, df_cutoff):
        if self.load_initial:
            df = self.backfill_helper(
                generate_query, 
                filename_curve_liquidity, 
                df_cutoff.cutoff.min()
                )
            return None
        return None

    def forward_filler(self):
        """
        Specifically doesn't fetch forward if also fetching initial to prevent timeouts
        """
        if self.should_fetch:
            if not self.load_initial:
                fetch(False)
        return get_df_from_file(filename_curve_liquidity)

    def join_cutoff(self, df, df_cutoff):
        df_cutoff = self.format_cutoff(df_cutoff)
     
        return pd.concat([df, df_cutoff])

    def format_cutoff(self, df_cutoff):
        cutoff = df_cutoff.cutoff.min()
        if not 'T' in cutoff:
            cutoff = cutoff.replace(' ', 'T')
        if not '.' in cutoff:
            cutoff = cutoff + '.000Z'
        if not 'Z' in cutoff:
            cutoff = cutoff + 'Z'
        df_cutoff['cutoff'] = cutoff
        df_cutoff = df_cutoff.rename(columns={
            "cutoff": 'block_timestamp',
            })   
        return df_cutoff

    """
    Since remote hosting has limits on how long processes can run
    no longer fully backfilling, but still merging first query
    """
    def backfill_helper(self, generate_query, filename, cutoff_time = None, page_size=10000):
        # Loop Basics
        # should_continue = True
        # try:
        #     df = get_df_from_file(filename)
        # except:
        #     df = []
        # Controls ending at a fixed cutoff
        if cutoff_time:
            cutoff_time = get_datetime_obj(cutoff_time)
        # while should_continue:
        # if len(df) == 0:
        # df = []
        # print("no starting position")
        if not cutoff_time:
            cutoff_time =  '2023-01-01 00:00:01'
        start_time = get_datetime_obj(cutoff_time)
        end_time = start_time + timedelta(days=8*7)
        # else:
        #     end_time = get_datetime_obj(df['block_timestamp'].min())
        #     start_time = end_time - timedelta(days=8*7)
            # if cutoff_time and start_time < cutoff_time:
            #     start_time = cutoff_time
            #     print("Last Run!")
        
        # Just cause looping paid queries, sometimes good to be able to manually cancel.
        # if self.human_management:
        #     user_input = self.user_control_check(start_time, end_time)
        #     if len(user_input) > 0:
        #         break
        # current_length = len(df)
        query = generate_query(start_time, end_time)
        df = query_and_save(query, filename, [], page_size)
            # if start_time == cutoff_time:
            #     should_continue = False
            # if len(df) < current_length:
            #     should_continue = False

        return df

    def user_control_check(self, start_time, end_time):
        # Begin true sequence
        print("="*50)
        print("="*50)
        print("GO BACK")
        print(f"Time Bounds: {start_time} --> {end_time}")
        # If things go off the rails, allow user to abort
        #   * Provides time to check in on api provider
        print("^^^ Look Up ^^^ User Input Requested ^^^")
        return input("Type anything to abort, or enter to continue")

