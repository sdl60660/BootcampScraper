#Takes in a search query with flags, keys, sometimes file date. Sends data from file and keys to revised_search.py.
#Receives an object back with filtered category data, list, summary, sort. Decides what to return based on flags.

import utilities
from utilities import return_closest
import json, sys, os, fnmatch
import argparse
from pprint import pprint
import os.path
import datetime

import revised_search
from revised_search import main
from revised_search import Camp_Info


def find_file(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

def date_to_file(date):
    dates = date.split('/')
    if len(dates) == 2:
        month = dates[0]
        day = dates[1]
        year = str(datetime.datetime.now().year)
    elif len(dates) == 3:
        month = dates[0]
        day = dates[1]
        year = dates[2]
        if len(year) == 2:
            year = '20' + year
    else:
        return 'NO_FILE'

    if len(month) == 1:
        month = '0' + month
    if len(day) == 1:
        day = '0' + day

    filedate = year + '-' + month + '-' + day + '.*'
    try:
        filename = find_file(filedate,'old_data/full_outputs/')[-1]
    except IndexError:
        return 'NO_FILE'
    return filename

def check_flag(flag, arg_list):
    boolean = False
    for arg in range(len(arg_list)):
        if arg_list[arg] == flag:
            boolean = True
            arg_list.remove(flag)
            break
    return boolean, arg_list

def main(search_keys):
    tracking_groups = ['Current Market', 'Potential Market', 'Top Camp', 'Java/.NET', 'Selected Camp']
    tracking_groups_files = find_file('*.json','current_data/tracking_groups')

    #COMMAND LINE OPTION PROCESSING
    or_flag, search_keys = check_flag('--or', search_keys)
    summary_flag, search_keys = check_flag('--summary', search_keys)
    list_flag, search_keys = check_flag('--list', search_keys)
    sort_flag, search_keys = check_flag('--sort', search_keys)
    custom_file, search_keys = check_flag('--file', search_keys)

    if custom_file == True:
        datafile = search_keys[1]
        search_keys.remove(search_keys[1])
        if len(datafile) < 12:
            datafile = date_to_file(datafile)
        if os.path.isfile(datafile) == False:
            print 'Could not find the specified file, switching to default data file.'
            datafile = 'current_data/output.json'

    if custom_file == False:
        datafile = 'current_data/output.json'

    result_data = revised_search.main(sys.argv)
    pprint(result_data.summary)


if __name__ == '__main__':
    main(sys.argv)