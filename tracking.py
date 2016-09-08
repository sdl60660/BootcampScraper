import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

import numpy as np
#import matplotlib.pyplot as plt
import os, fnmatch
import sys

import json
import jsonmerge

import filecmp

def find_file(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

def generate_filename(date):
    date_input = str(date) + '.*'
    print date_input
    filename = find_file(date_input,'old_data/full_outputs/')[-1]
    return filename

def load_date_data(today_ordinal, ordinal_back):
    target_date = date.fromordinal(today_ordinal - ordinal_back)
    filename = generate_filename(target_date)
    with open(filename, 'rb') as current_data:
        data = json.load(current_data)
    return data


today = date.today()
today_ordinal = today.toordinal()

#OPEN CURRENT FILE
with open('current_data/output.json', 'rb') as current_data:
    data_today = json.load(current_data)

#OPEN FILE FROM YESTERDAY (TAKE TODAY'S ORDINAL DATE, SUBTRACT 1, FIND DATE, USE TO FIND FILE)
try:
    if today.weekday() == 0:
        data_yesterday = load_date_data(today_ordinal, 3)
    else:
        data_yesterday = load_date_data(today_ordinal, 1)
except IndexError:
    print "No data in file for this date yesterday."
    pass


#OPEN FILE FROM ONE WEEK AGO (TAKE TODAY'S ORDINAL DATE, SUBTRACT 7, FIND DATE, USE TO FIND FILE)
try:
    data_last_week = load_date_data(today_ordinal, 7)
except IndexError:
    print "No data in file for this date last week."
    pass


#OPEN FILE FROM ONE MONTH AGO (ROUND TO NEAREST WEEKDAY*)
last_month = date.today() + relativedelta(months=-1)
if last_month.weekday() == 6:
    last_month = last_month + relativedelta(days=+1)
elif last_month.weekday() == 5:
    last_month = last_month + relativedelta(days =-1)
lm_days_back = (today_ordinal - last_month.toordinal())
try:
    data_last_month = load_date_data(today_ordinal, lm_days_back)
except IndexError:
    print "No data in file for this date last month."
    pass


#OPEN FILE FROM ONE YEAR AGO (ROUND TO NEAREST WEEKDAY*)
last_year = date.today() + relativedelta(years=-1)
if last_year.weekday() == 6:
    last_year = last_year + relativedelta(days=+1)
elif last_year.weekday() == 5:
    last_year = last_year + relativedelta(days =-1)
ly_days_back = (today_ordinal - last_year.toordinal())
try:
    load_date_data(today_ordinal, ly_days_back)
except IndexError:
    print "No data in file for this date last year."
    pass

#*GET RID OF THIS PART IF YOU EVER END UP RUNNING THIS ON WEEKEND DAYS

class Trackers:

    def tracked_location_moves():
        pass


    def tracking_group_stats():
        pass


    def tracking_group_changes():
        pass


    def technology_trends():
        pass


    def location_trends():
        pass







