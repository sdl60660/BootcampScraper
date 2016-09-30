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
import slack_output
from current_data import attribute_dict
#from slack_output import slack_output


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

#1. COMPLETE SECTION TO FEED OUT SLACKBOT SEARCH
#2. ADD PLOTTER OPTION FUNCTIONALITY ON THE WRAPPER END (CALL GENERATE_PLOT FUNCTION AND RETURN PLOT TO SLACK/CONSOLE)
#3. AND/OR OPTIONS ON WRAPPER END
#4. ~~~IN PROGRESS~~~ MAP SEARCH TERMS TO JSON TERMS USING ATTRIBUTE DICT

def main(search_keys):
    print "Need to finish search term translations!!!"
    sys.exit()
    #========IN PROGRESS========#
    for i, term in enumerate(search_keys):
        if term in attribute_dict.In_Dict.keys():
            search_keys[i] = attribute_dict.In_Dict[term]
    #========IN PROGRESS========#
    tracking_groups = ['Current Market', 'Potential Market', 'Top Camp', 'Java/.NET', 'Selected Camp']
    tracking_groups_files = find_file('*.json','current_data/tracking_groups')

    #print search_keys

    if search_keys[-1] == 'Slack':
        search_keys.remove('Slack')
        source = 'Slack'
    else:
        source = 'Terminal'

    #COMMAND LINE OPTION PROCESSING
    or_flag, search_keys = check_flag('--or', search_keys)
    summary_flag, search_keys = check_flag('--summary', search_keys)
    list_flag, search_keys = check_flag('--list', search_keys)
    sort_flag, search_keys = check_flag('--sort', search_keys)
    warnings_flag, search_keys = check_flag('--warnings', search_keys)
    custom_file, search_keys = check_flag('--file', search_keys)
    plot_flag, search_keys = check_flag('--plot', search_keys)

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

    if source == 'Terminal':
        if summary_flag == True:
            print'\n================================================================================\n' \
            'SUMMARY: Breakdown of specified categories (Total Camps in Query: ' + str(len(result_data.camps)) + ')\n'
            for cat in result_data.summary:
                if cat != 'warning':
                    pprint(result_data.summary[cat])
            if warnings_flag == True:
                print
                print 'WARNING: THESE CAMPS FIT THE SPECIFIED FILTERS, BUT DID NOT HAVE DATA FOR THE FOLLOWING CATEGORIES'
                pprint(result_data.summary['warning'])

        if sort_flag == True:
            print '\n===============================================================================================\n' \
            'SORT: Sorted list of camps by specified categories\n'
            for cat in result_data.sort:
                if cat != 'warning':
                    print cat.title() + ':'
                    pprint(result_data.sort[cat])
                    print
            if warnings_flag == True:
                print
                print 'WARNING: THESE CAMPS FIT THE SPECIFIED FILTERS, BUT DID NOT HAVE DATA FOR THE FOLLOWING CATEGORIES'
                pprint(result_data.sort['warning'])

        if list_flag == True:
            print '\n===============================================================================================\n' \
            'LIST: The following bootcamps fit the inputed tracking group, location, and technology filters (Total Camps in Query: ' + str(len(result_data.camps)) + ')\n'
            pprint(result_data.camp_list)
    else:
        slack_formatted_output = slack_output.slack_output(result_data)

if __name__ == '__main__':
    main(sys.argv)