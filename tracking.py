import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from closest import return_closest

import numpy as np
#import matplotlib.pyplot as plt
import os, fnmatch
import sys

import json
import jsonmerge

import filecmp

tracking_groups = ['Java/.NET', 'Potential Markets', 'Current Markets', 'Top Camp', 'Selected Camp']

def find_file(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

def generate_filename(date):
    date_input = str(date) + '.*'
    filename = find_file(date_input,'old_data/full_outputs/')[-1]
    return filename

def load_date_data(today_ordinal, ordinal_back):
    target_date = date.fromordinal(today_ordinal - ordinal_back)
    if target_date.weekday() == 6:
        target_date = date.fromordinal(today_ordinal - ordinal_back + 1)
    elif target_date.weekday() == 5:
        target_date = date.fromordinal(today_ordinal - ordinal_back - 1)
    try:
        filename = generate_filename(target_date)
    except IndexError:
        print 'Sorry! No file found for that date. Please enter a new one.'
        sys.exit()
    with open(filename, 'rb') as current_data:
        data = json.load(current_data)
    return data


today = date.today()
today_ordinal = today.toordinal()

#OPEN CURRENT FILE
with open('current_data/output.json', 'rb') as current_data:
    bootcamps = json.load(current_data)


def tracked_camp_changes(days_back, category, tracking_group='ALL'):
    today = date.today()
    today_ordinal = today.toordinal()

    new_points = []

    old_data = load_date_data(today_ordinal, days_back)

    for x in bootcamps:
        camp = bootcamps[x]
        if x == 'meta':
            continue
        if camp[category] == None:
                continue
        if tracking_group == 'ALL':
            pass
        elif tracking_group not in camp['tracking_groups']:
            continue

        for item in camp[category]:
            if item not in old_data[x][category]:
                new_points.append((item, x))
    print
    return new_points


def tracking_group_stats():
    pass


def tracking_group_changes():
    pass


def meta_category_trend():
    pass


def full_meta_trends():
    pass

"""

#OPEN FILE FROM ONE YEAR AGO (ROUND TO NEAREST WEEKDAY*)
last_year = date.today() + relativedelta(years=-1)
if last_year.weekday() == 6:
    last_year = last_year + relativedelta(days=+1)
elif last_year.weekday() == 5:
    last_year = last_year + relativedelta(days =-1)
ly_days_back = (today_ordinal - last_year.toordinal())
try:
    data_last_year = load_date_data(today_ordinal, ly_days_back)
except IndexError:
    print "No data in file for this date last year."
    pass
"""






