from flask import current_app as app
from app.data.reference import filename_actors

from app.data.local_storage import (
    pd,
    # read_json,
    # read_csv,
    # write_dataframe_csv,
    # write_dfs_to_xlsx,
    csv_to_df
    )


from app.utilities.utility import (
    # get_period_direct, 
    # get_period_end_date, 
    get_date_obj, 
    get_dt_from_timestamp,
    nullify_amount
    # shift_time_days,
    # df_remove_nan
)

from app.convex.delegations.process_flipside import process_and_get

print("Loading... { address_book.actors.models }")


def format_df(df):
    # pass
    return df

def get_df(filename, location):
    df = csv_to_df(filename, location)
    df = format_df(df)
    return df

df_actors = get_df(filename_actors, 'processed')


try:
    app.config['df_actors'] = df_actors

except:
    print("could not register in app.config\n\Address Book Actors")



