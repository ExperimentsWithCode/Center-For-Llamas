from datetime import datetime as dt
from datetime import date, timedelta, tzinfo
import numpy as np
from functools import wraps
from time import time
from app.data.local_storage import (
    pd,
    cwd
    )
from app.data.reference import models_split_into_folders

try:
    from config import activate_print_mode
except:
    activate_print_mode = False

import PIL
import io

def print_mode(to_print):
    if activate_print_mode:
        print(to_print)
    


def timed(f):
  @wraps(f)
  def wrapper(*args, **kwds):
    start = time()
    result = f(*args, **kwds)
    elapsed = time() - start
    if activate_print_mode:
        print_mode("-"*50)
        print_mode ("\t%s took \n\t\t%d time to finish" % (f.__name__, elapsed))
        print_mode("-"*50)
    return result
  return wrapper

def df_remove_nan(df):
    return df.where(pd.notnull(df), None)



## Datetime stuff
ZERO = timedelta(0)

class UTC(tzinfo):
  def utcoffset(self, dt):
    return ZERO
  def tzname(self, dt):
    return "UTC"
  def dst(self, dt):
    return ZERO

utc = UTC()

def get_now():
    return get_datetime_obj(dt.utcnow())

def shift_time_days(time, days=7, forward=True):
    time = get_date_obj(time)
    if forward:
        return time  + timedelta(days=days)
    else:
        return time  - timedelta(days=days)



def get_date_obj(time):
    return get_datetime_obj(time)
    # if type(time) == str:
    #     if len(time) == 0:
    #         return None
    #     if 'T' in time:
    #         try:
    #             split = time.split("T")
    #             time = split[0]+" "+split[1][:-1]
    #             # row['block_timestamp'] = dt.strptime(row['block_timestamp'], '%Y-%m-%d %H:%M:%S.%f'),
    #         except:
    #             pass
    #     try:
    #         time = dt.strptime(time,'%Y-%m-%d %H:%M:%S.%f')
    #     except:
    #         time = dt.strptime(time,'%Y-%m-%d %H:%M:%S')      
    # return time

def get_dt_from_timestamp(timestamp):
    if type(timestamp) == str:
        if len(timestamp) <= 8:
            return None
        if '.' in timestamp:
            timestamp = timestamp[:timestamp.find('.')]
    return dt.fromtimestamp(int(timestamp)).replace(tzinfo=utc)

# Attempts to be timezone aware
# updated get_date_obj which can handle more variance
def get_datetime_obj(time):
    if type(time) == str:
        if len(time) == 0:
            return None
        if 'T' in time:
            try:
                split = time.split("T")
                time = split[0]+" "+split[1][:-1]
            except:
                pass
        if '.' in time:
            try:
                split = time.split(".")
                time = split[0]
            except:
                pass
        if '+' in time:
            try:
                split = time.split('+')
                time = split[0]
            except:
                pass

        try:
            time = dt.strptime(time,'%Y-%m-%d %H:%M:%S.%f')
        except:
            time = dt.strptime(time,'%Y-%m-%d %H:%M:%S')   
    # elif type(time) == date:
    #     year = str(time.year) 
    #     month = str(time.month) if time.month >= 10 else "0"+ str(time.month)
    #     day = str(time.day) if time.day >= 10 else "0"+ str(time.day)
    #     time_string = f"{year}-{month}-{day} 23:59:59-UTC"
    #     time = dt.strptime(time_string, '%Y-%m-%d %H:%M:%S-%Z')
    return time.replace(tzinfo=utc)

# Slight issue on splitting years will split period despite single period.
def get_period(week_num, week_day, time, target=5):
    if week_num > -1 and week_day > -1:
        time = get_date_obj(time)
        week_num = int(time.strftime("%V"))
        week_day = int(time.weekday())
        vote_year = time.year
        if time.month == 1 and week_num == 52:
            week_num = 0
        if week_day >= target:
            week_num = week_num + 1
        else:
            week_num = week_num
        if week_num < 10 or week_num == 0:
            week_num = f"0{week_num}"
        return f"{vote_year}.{week_num}"
    # print('WEEK NOT FOUND')
    # print(week_day)
    # print(week_num)
    return "0"


# Slight issue on splitting years will split period despite single period.
def get_period_direct(time, target=5):
    time = get_date_obj(time)

    week_num = int(time.strftime("%V"))
    week_day = int(time.weekday())      # starts sunday
    vote_year = time.year
    if time.month == 1 and week_num == 52:
        week_num = 0
    if week_day >= target:
        week_num = week_num + 1
    else:
        week_num = week_num
    if week_num < 10:
        week_num = f"0{week_num}"
    # elif week_num % 10 = 0:
    return f"{vote_year}.{week_num}"
    # print('WEEK NOT FOUND')
    # print(week_day)
    # print(week_num)
    # return 0

def get_convex_period_direct(time, target=5):
    # print(time)
    # print(type(time))
    time = get_date_obj(time)
    week_num = int(time.strftime("%V"))
    week_day = int(time.weekday())      # starts sunday
    vote_year = time.year
    if time.month == 1 and week_num == 52:
        week_num = 0
    if week_day >= target:
        week_num = week_num + 1
    else:
        week_num = week_num
    if week_num % 2 == 1:
        week_num += 1
    if week_num < 10 or week_num == 0:
        week_num = f"0{week_num}"
    # elif week_num % 10 = 0:
    return f"{vote_year}.{week_num}"

def get_checkpoint_end_date(this_time):
    # set day to upcoming thursday
    x = get_date_obj(this_time)
    week_day = int(x.weekday())
    if week_day >= 4:
        week_day_adj = 4 + (7 - week_day)
    else:
        week_day_adj = 4 - week_day
    return x + timedelta(days=week_day_adj)

# Slow replace w/ above once function 
#   Is wrong about year changes
def get_period_end_date(time):
    # this is terrible. 
    # I know its terrible. 
    # I think fromisocalendar starts on monday?
    time = get_date_obj(time)

    week_num = int(time.strftime("%V"))
    week_day = int(time.weekday())      # starts sunday

    month = int(time.month)
    year = int(time.year)
    if week_num > 50 and month == 1:
        week_num = 1
    if week_day >= 5:
        week_num += 1
    # print(time)
    
    try:
        date_out = date.fromisocalendar(time.year, week_num, 1) 
    except:
        date_out = date.fromisocalendar(time.year, week_num-1, 1) 
        date_out = date_out  + timedelta(days=7)
    return date_out +  timedelta(days=3)


def concat_all(df_list, sort_list = ["this_period"]):
    df_concat = None
    first = True
    for df in df_list:
        if first:
            df_concat = df
            first = False
            continue
        df_concat = pd.concat([df_concat, df])
    df_concat = df_concat.sort_values(sort_list, axis = 0, ascending = False)
    return df_concat


def format_plotly_figure(fig, _height=None):
    fig.update_layout(
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="RebeccaPurple"
        ),
        height= _height,
    )
    return fig

def format_plotly_animation(fig):
    fig.update_layout(
    updatemenus=[dict(buttons = [
        dict(
            args = [None, {"frame": {"duration": 2000, 
                                    "redraw": True},
                            "fromcurrent": False, 
                            "transition": {"duration": 500, "easing": "quadratic-in-out"}}],
            label = "Play",
            method = "animate"
            ),
        dict(
            args = [[None], {"frame": {"duration": 0, 
                                    "redraw": False},
                            "mode": "immediate",
                            "transition": {"duration": 0}}],
            label = "Stop",
            method = "animate"
            ),
        ],
        type='buttons',
        showactive=True,
        y=1,
        x=1.12,
        xanchor='left',
        yanchor='bottom',

        )]
    )
    return fig

def convert_animation_to_gif(fig, fig_name, path='app/generated_images/'):
    # generate images for each step in animation
    frames = []
    for s, fr in enumerate(fig.frames):
        # set main traces to appropriate traces within plotly frame
        fig.update(data=fr.data)
        fig.update(layout=fr.layout)
        # move slider to correct place
        fig.layout.sliders[s].update(active=s)
        # fig.layout.title[0].update(active=fr.)
        # generate image of current state
        frames.append(PIL.Image.open(io.BytesIO(fig.to_image(format="png"))))
        
    # create animated GIF
    frames[0].save(
            f"{cwd}/{path}{fig_name}.gif",
            save_all=True,
            append_images=frames[1:],
            optimize=True,
            duration=500,
            loop=1,
        )

def get_address_profile(df, target):
    return df[df['address'] == target]
# def calc_lock_efficiency(action_time, final_lock_time):
#     # if type(action_time) == str:
#     action_time = get_checkpoint_timestamp(action_time)
#     # action_time = action_time.date
#     # if type(final_lock_time) == str:
#     #     final_lock_time = get_checkpoint_timestamp(final_lock_time)
#     #     # final_lock_time = final_lock_time.date
#     # else:
#     #     final_lock_time =  final_lock_time.date()
#     final_lock_time = get_checkpoint_timestamp(final_lock_time)
#     # 4 years forward date
#     four_years_forward = action_time + timedelta(seconds=365 * 4 * 86400)
#     # four_years_forward = four_years_forward.date()

#     # time deltas
#     diff_lock_time = final_lock_time - action_time
#     diff_max_lock = four_years_forward - action_time

#     # ratio
#     ## Add 1 to offset locks week of max lock are max locked
#     lock_weeks = int((diff_lock_time / pd.Timedelta(seconds= 7 * 86400)))
#     max_weeks = int(diff_max_lock / pd.Timedelta(seconds= 7 * 86400))

#     if lock_weeks / max_weeks > 1:
#         print(f"Lock Efficiency: {action_time}, {final_lock_time}")
#     return lock_weeks / max_weeks if lock_weeks / max_weeks <= 1 else 1

def get_lock_diffs(final_lock_time):
    action_time = get_checkpoint_timestamp(dt.utcnow())

        # action_time = action_time.date
    # if type(final_lock_time) == str:
    #     final_lock_time = get_checkpoint_end_date(final_lock_time)
    #     # final_lock_time = final_lock_time.date
    # else:
    #     final_lock_time =  final_lock_time.date()
    #     final_lock_time = get_checkpoint_end_date(final_lock_time)
    final_lock_time = get_checkpoint_timestamp(final_lock_time)
    # 4 years forward date
    four_years_forward = action_time + timedelta(seconds=365 * 4 * 86400)
    # four_years_forward = four_years_forward.date()

    # time deltas
    diff_lock_time = final_lock_time - action_time 
    diff_max_lock = four_years_forward - action_time

    # ratio
    ## Add 1 to offset locks week of max lock are max locked
    lock_weeks = int((diff_lock_time / pd.Timedelta(days=7)))
    max_weeks = int(diff_max_lock / pd.Timedelta(days=7))
    
    return int(lock_weeks), int(max_weeks)

def nullify_amount(value):
    if value == 'null' or value == '' or value == '-':
        return np.nan
    return float(value)

def nullify_list(value, is_unique=False):
    if type(value) == float:
        return []
    elif is_unique:
        return list(set(value))
    else:
        return value

def convert_units(value, decimals=18):
    ignore_values = ['null', '', '-', None]
    if value in ignore_values:
        return np.nan
    return float(int(float(value)) / 10**decimals)

"""
Checkpoints
"""
# Needs more dynamic generation
def generate_checkpoints(start_time = '2020-08-12 10:33:20+00:00'):
    week =  7 * 86400 
    start_date = get_datetime_obj(start_time)
    print_mode(start_date)
    #
    i = 0
    checkpoints = []
    checkpoint_date = start_date
    # 181 is weak input. Fix.
    while i < (181 + 52*8):
        # print(checkpoint_date)
        checkpoints.append({
            'id': i, 
            'checkpoint_timestamp': checkpoint_date
            })
        i += 1
        checkpoint_date = start_date + timedelta(seconds = week*i)
    return checkpoints

df_default_checkpoints = pd.json_normalize(generate_checkpoints())

# def get_checkpoint(timestamp, df_checkpoints = df_default_checkpoints):
#     time_obj = get_datetime_obj(timestamp)
#     date_diff = time_obj - df_checkpoints.checkpoint_timestamp.min() 
#     try:
#         this_id = round(date_diff.days / 7)
#     except:
#         print(timestamp)
#         print(time_obj)
#         print(df_checkpoints.checkpoint_timestamp.min())
#         print(date_diff)
#         this_id = 0
#     if this_id < 1:
#         this_id = 0
#     # print(f"id: {this_id}")
#     this_checkpoint = df_checkpoints[df_checkpoints['id'] == this_id]
#     # print(this_checkpoint)
#     try:
#         while this_checkpoint.iloc[0].checkpoint_timestamp < time_obj:
#             this_id += 1
#             this_checkpoint = df_checkpoints[df_checkpoints['id'] == this_id]
#         while this_checkpoint.iloc[0].checkpoint_timestamp > time_obj:
#             this_id -= 1
#             temp_checkpoint = df_checkpoints[df_checkpoints['id'] == this_id]
#             if len(temp_checkpoint) > 0:
#                 if temp_checkpoint.iloc[0].checkpoint_timestamp < time_obj:
#                     break
#                 else:
#                     this_checkpoint.iloc[0].checkpoint_timestamp = temp_checkpoint
#             else:
#                 break
#         return this_checkpoint.iloc[0]
#     except Exception as e:
#         print(e)
#         print(timestamp)
#         print(f"ID: {this_id}")
#         return None

# def get_checkpoint_id(timestamp):
#     this_checkpoint = get_checkpoint(timestamp)
#     return this_checkpoint.id


def get_checkpoint(timestamp, df_checkpoints = df_default_checkpoints):
    this_id = get_checkpoint_id(timestamp, df_checkpoints)
    # print(f"id: {this_id}")
    this_checkpoint = df_checkpoints[df_checkpoints['id'] == this_id]
    # print(this_checkpoint)
   
    return this_checkpoint.iloc[0]



def get_checkpoint_id(timestamp, df_checkpoints = df_default_checkpoints):
    time_obj = get_datetime_obj(timestamp)
    date_diff = time_obj - df_checkpoints.checkpoint_timestamp.min() 
    try:
        seconds_diff_as_days = date_diff.seconds / 60 / 60 / 24
        this_id = int((date_diff.days + seconds_diff_as_days ) / 7)
    except Exception as e:
        print(e)
        print('\t @ app/utility/utilitie > get_checkpoint_id')
        print_mode(f"Timestamp: {timestamp}")
        print_mode(f"Min Checkpoint: {df_checkpoints.checkpoint_timestamp.min()}")
        print_mode(f"Date Diff: {date_diff}")
        this_id = 0
    if this_id < 1:
        this_id = 0
    # int rounds down.
        # but first round is 0
        # this makes checkpoint 1 ahead
    this_id+=1  #
    return this_id

def get_checkpoint_timestamp(timestamp):
    this_checkpoint = get_checkpoint(timestamp)
    return this_checkpoint.checkpoint_timestamp

def get_checkpoint_timestamp_from_id(id, df_checkpoints = df_default_checkpoints):
    this_checkpoint = df_checkpoints[df_checkpoints['id'] == id]
    return this_checkpoint.iloc[0].checkpoint_timestamp

def get_checkpoint_id_from_date(input_date, df_checkpoints = df_default_checkpoints):
    this_checkpoint = df_checkpoints[df_checkpoints['checkpoint_timestamp'].dt.date < input_date]
    return this_checkpoint.iloc[-1].id 

def get_checkpoint_timestamp_from_date(input_date, df_checkpoints = df_default_checkpoints):
    this_checkpoint = df_checkpoints[df_checkpoints['checkpoint_timestamp'].dt.date < input_date]
    return this_checkpoint.iloc[-1].checkpoint_timestamp 

def calc_lock_efficiency_by_checkpoint(action_checkpoint, final_lock_checkpoint):

    # 4 years forward date
    max_lock_diff = int(365 * 4 / 7) - 1
    checkpoint_diff = final_lock_checkpoint - action_checkpoint
    if checkpoint_diff < 0:
        return 0
    # four_years_forward = action_checkpoint + timedelta(seconds=365 * 4 * 86400)
    # four_years_forward = four_years_forward.date()

    # ratio
    ## Add 1 to offset locks week of max lock are max locked
    # lock_weeks = int((max_lock_diff / pd.Timedelta(seconds= 7 * 86400)))
    # max_weeks = int(diff_max_lock / pd.Timedelta(seconds= 7 * 86400))

    if checkpoint_diff / max_lock_diff > 1:
        # print(f"Checkpoint Diff {action_checkpoint}, {final_lock_checkpoint}")
        efficiency = 1
    else:
        efficiency = checkpoint_diff / max_lock_diff

    return efficiency

