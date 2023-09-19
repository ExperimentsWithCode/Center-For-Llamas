from datetime import datetime as dt
from datetime import date, timedelta

from functools import wraps
from time import time


def timed(f):
  @wraps(f)
  def wrapper(*args, **kwds):
    start = time()
    result = f(*args, **kwds)
    elapsed = time() - start
    print ("\t%s took \n\t\t%d time to finish" % (f.__name__, elapsed))
    return result
  return wrapper


# Slight issue on splitting years will split period despite single period.
def get_period(week_num, week_day, time, target=5):
    if week_num > -1 and week_day > -1:
        if type(time) == str:
            time = dt.strptime(time,'%Y-%m-%d %H:%M:%S.%f')
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
    if type(time) == str:
        time = dt.strptime(time,'%Y-%m-%d %H:%M:%S.%f')
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
    if type(time) == str:
        time = dt.strptime(time,'%Y-%m-%d %H:%M:%S.%f')
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

def get_period_end_date(time):
    # this is terrible. 
    # I know its terrible. 
    # I think fromisocalendar starts on monday?
    if type(time) == str:
        time = dt.strptime(time,'%Y-%m-%d %H:%M:%S.%f')
    week_num = int(time.strftime("%V"))
    week_day = int(time.weekday())      # starts sunday

    day = int(time.day)
    month = int(time.month)
    if week_num > 50 and month == 1:
        week_num = 1
    if week_day > 5:
        week_num += 1
    # print(time)
    try:
        date_out = date.fromisocalendar(time.year, week_num, 1) 
    except:
        date_out = date.fromisocalendar(time.year, week_num-1, 1) 
        date_out = date_out  + timedelta(days=7)
    return date_out +  timedelta(days=3)
