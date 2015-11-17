__author__ = 'SARA'

import time, datetime

def getUnixNow():
    return time.time()

# created_time is in UNIX time format
# convert it into human readable format
def convert_time_unix_to_human(input_time):
    # return time.strftime("%Y-%m-%d %H:%M", time.localtime(int(input_time)))
    return time.strftime("%Y-%m-%d", time.localtime(int(input_time)))

def convert_human_to_unix(input_time):
    return time.mktime(input_time.timetuple())

def format_date(input_datetime):
    return datetime.datetime.strptime(input_datetime, "%Y-%m-%d")

def convert_datetime(input_datetime):
    return input_datetime[0:4] + '-' + input_datetime[4:6] + '-' + input_datetime [6:8] \
           + ' ' + input_datetime[8:10] + ':' + input_datetime[10:12] + ':' + input_datetime[12:14]
