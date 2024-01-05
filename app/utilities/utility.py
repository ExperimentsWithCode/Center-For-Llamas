from datetime import datetime as dt
from datetime import date, timedelta

from functools import wraps
from time import time
from app.data.local_storage import (
    pd,
    )

import PIL
import io

def timed(f):
  @wraps(f)
  def wrapper(*args, **kwds):
    start = time()
    result = f(*args, **kwds)
    elapsed = time() - start
    print ("\t%s took \n\t\t%d time to finish" % (f.__name__, elapsed))
    return result
  return wrapper

def df_remove_nan(df):
    return df.where(pd.notnull(df), None)

def shift_time_days(time, days=7, forward=True):
    time = get_date_obj(time)
    if forward:
        return time  + timedelta(days=days)
    else:
        return time  - timedelta(days=days)



def get_date_obj(time):
    if type(time) == str:
        if len(time) == 0:
            return None
        if 'T' in time:
            try:
                split = time.split("T")
                time = split[0]+" "+split[1][:-1]
                # row['block_timestamp'] = dt.strptime(row['block_timestamp'], '%Y-%m-%d %H:%M:%S.%f'),
            except:
                pass
        try:
            time = dt.strptime(time,'%Y-%m-%d %H:%M:%S.%f')
        except:
            time = dt.strptime(time,'%Y-%m-%d %H:%M:%S')      
    return time

def get_dt_from_timestamp(timestamp):
    if len(timestamp) == 0:
        return None
    if '.' in timestamp:
        timestamp = timestamp[:timestamp.find('.')]
    return dt.fromtimestamp(int(timestamp))

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
    print('WEEK NOT FOUND')
    print(week_day)
    print(week_num)
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
    if _height:
        fig.update_layout(
            font=dict(
                family="Courier New, monospace",
                size=14,
                color="RebeccaPurple"
            ),
            # height= 1000,
        )
    else:
        fig.update_layout(
            font=dict(
                family="Courier New, monospace",
                size=14,
                color="RebeccaPurple"
            ),
            height= _height,
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
        fig.layout.sliders[0].update(active=s)
        # fig.layout.title[0].update(active=fr.)
        # generate image of current state
        frames.append(PIL.Image.open(io.BytesIO(fig.to_image(format="png"))))
        
    # create animated GIF
    frames[0].save(
            f"{path}{fig_name}.gif",
            save_all=True,
            append_images=frames[1:],
            optimize=True,
            duration=500,
            loop=1,
        )
    
def calc_lock_efficiency(action_time, final_lock_time):
    # if type(action_time) == str:
    action_time = get_checkpoint_end_date(action_time)
    # action_time = action_time.date
    if type(final_lock_time) == str:
        final_lock_time = get_checkpoint_end_date(final_lock_time)
        # final_lock_time = final_lock_time.date
    else:
        final_lock_time =  final_lock_time.date()
        final_lock_time = get_checkpoint_end_date(final_lock_time)
    # 4 years forward date
    four_years_forward = action_time + timedelta(days=(365 * 4))
    # four_years_forward = four_years_forward.date()

    # time deltas
    diff_lock_time = final_lock_time - action_time
    diff_max_lock = four_years_forward - action_time

    # ratio
    ## Add 1 to offset locks week of max lock are max locked
    lock_weeks = int((diff_lock_time / pd.Timedelta(days=7)))
    max_weeks = int(diff_max_lock / pd.Timedelta(days=7))

    if lock_weeks / max_weeks > 1:
        print(action_time, final_lock_time)
    return lock_weeks / max_weeks if lock_weeks / max_weeks <= 1 else 1

def get_lock_diffs(final_lock_time):
    dt.now()
    action_time = dt.now().date()
        # action_time = action_time.date
    if type(final_lock_time) == str:
        final_lock_time = get_checkpoint_end_date(final_lock_time)
        # final_lock_time = final_lock_time.date
    else:
        final_lock_time =  final_lock_time.date()
        final_lock_time = get_checkpoint_end_date(final_lock_time)
    # 4 years forward date
    four_years_forward = action_time + timedelta(days=(7 * 52 * 4))
    # four_years_forward = four_years_forward.date()

    # time deltas
    diff_lock_time = final_lock_time - action_time 
    diff_max_lock = four_years_forward - action_time

    # ratio
    ## Add 1 to offset locks week of max lock are max locked
    lock_weeks = int((diff_lock_time / pd.Timedelta(days=7)))
    max_weeks = int(diff_max_lock / pd.Timedelta(days=7))
    
    return int(lock_weeks), int(max_weeks)