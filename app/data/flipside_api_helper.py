from flipside import Flipside
from config import flipside_api_key, flipside_nft_holder_address

import pandas as pd

from app.utilities.utility import print_mode
from app.data.local_storage import (
    read_json,
    read_csv,
    write_dataframe_csv
)

sdk = Flipside(flipside_api_key)


# data_path = "/app/data/source"


def print_metrics(query):
    started_at = query.run_stats.started_at
    ended_at = query.run_stats.ended_at
    elapsed_seconds = query.run_stats.elapsed_seconds
    record_count = query.run_stats.record_count
    print_mode(f"This query took ${elapsed_seconds} seconds to run and returned {record_count} records from the database.")


"""
Load Data Initial OR Update existing DF
"""
def query_and_save(_query, _filename, _df_base = [], _page_size = 5000):
    try:
        # Initial Query
        if len(_df_base) > 0:
            print_mode("based")
            df_output = _df_base
        else:
            df_output = []

        print_mode(f"___\n{_filename}")
        print_mode(f"querying page: 1")
        query_result_set = sdk.query(_query, page_size = _page_size)
        if len(df_output) == 0:
            df_output = pd.json_normalize(query_result_set.records)
        else:
            # Concat Dataframes
            df_local = pd.json_normalize(query_result_set.records)
            df_output = pd.concat([df_output, df_local], ignore_index=True)

        # Metrics
        print_metrics(query_result_set)
        i = 2
            
        # Handle Pagination
        if len(query_result_set.records) >= _page_size:
            keep_going = True
            while keep_going:
                print_mode(f"Querying Page: {i}")
                extended_result_set = sdk.get_query_results(
                    query_result_set.query_id,
                    page_number=i,
                    page_size=_page_size
                )
                # Metrics (don't provide novel info on new pages)
                print_mode(print_metrics(query_result_set))
                
                # Concat Dataframes
                df_local = pd.json_normalize(extended_result_set.records)
                df_output = pd.concat([df_output, df_local], ignore_index=True)
                
                # Check if continue
                result_length = len(extended_result_set.records) 
                print_mode(f"\tCompleted? {result_length} {result_length < _page_size} ")
                print_mode(len(extended_result_set.records) < _page_size)
                print_mode(len(extended_result_set.records))
                if len(extended_result_set.records) < _page_size:
                    keep_going = False
                i += 1
        # Save
        write_dataframe_csv(_filename, df_output, 'raw_data')
        print_mode('complete')
    except Exception as e:
        print(e)
        if len(_df_base) > 0:
            df_output = _df_base
        else:
            df_output = []

    return df_output


def get_df_and_target(filename, target = 'block_timestamp'):
    # gets dataframe and max value of target intended for time values
    resp_dict = read_csv(filename, 'raw_data')
    df = pd.json_normalize(resp_dict)
    print_mode(df.keys())

    # Get Max Value of target
    temp_df = df.sort_values(target).tail(1)
    search_result = temp_df.iloc[0][target] 
    df = df[df[target] < search_result]
    try:
        if 'T' in search_result:
            split = search_result.split("T")
            search_result = split[0]+" "+split[1][:-1]
    except:
        pass
    print_mode(search_result)
    return df, search_result


def fetch_and_save_data(filename, generate_query, fetch_initial = False, target = 'block_timestamp'):
    if fetch_initial:
        query = generate_query()
        df = query_and_save(query, filename)
    else:
        df, block_timestamp = get_df_and_target(filename, target)
        query = generate_query(block_timestamp)
        df = query_and_save(query, filename, df)
    return df


