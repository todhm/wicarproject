from itertools import product
import time
from datetime import datetime as dt
from datetime import timedelta,date
from iamport import Iamport
from flask import current_app,request,session
from application import db
from carbooking.models import UserCard, CarBooking, Payment, Message
from utilities.smsutil import send_sms,send_payment_error,send_lms
from utilities.hashutil import decrypt_hash, return_card_number


def timestamp():
    return time.mktime(dt.now().timetuple())

def get_current_day():
    return dt.now()

def get_end_day(day=7):
    return dt.now() + timedelta(days=day)


def get_time_comb(start_hour = 0):
    #['00:00'... '23:30']list 생성
    time_str = list(
                map(
                    lambda x: x[0] + ":" + x[1],
                    product(
                        map(
                            lambda x: str(x) if len(str(x))==2 else str(0) + str(x) ,
                            range(start_hour,24)
                            ),
                        ['00','30']
                        )))

    # 60*hour + minute의 값을갖는 integer list생성
    time_int = list(map(lambda x: x[0]*60 + x[1],product(range(start_hour,24),[0,30])))
    return_time = {}
    return_time['timeValue'] = time_int
    return_time['timeLabel'] = time_str
    return return_time


def get_hour_diff(dt1,dt2):
    diff = dt1-dt2
    days, seconds = diff.days, diff.seconds
    hours = days * 24 + seconds // 3600
    return hours

def get_next_week_by_day(daynum):
    monday = dt.now() + timedelta(days=7-dt.now().weekday())
    target_day=monday + timedelta(days=daynum)
    return target_day


def get_total_rental_days(start_time,end_time):
    td = end_time -start_time
    days,hours = td.days, td.seconds//3600
    days = 1 if days==0 else days
    if hours >=12 and days>1:
        days +=1
    return days

def find_duplicate_time(standard_start_time,standard_end_time,start_time,end_time):
    if start_time <= standard_start_time and end_time >= standard_start_time:
        return True
    elif start_time >= standard_start_time and start_time <= standard_end_time:
        return True
    else:
        return False


def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(days=n)

def rental_range(start_time,days):
    for n in range(days):
        yield start_time + timedelta(days=n)


def dow_convert(dow):
    dow_dict = {0:'월요일',1:'화요일',2:'수요일',3:'목요일',4:'금요일',
                5:'토요일',6:'일요일'}
    return dow_dict[dow]
