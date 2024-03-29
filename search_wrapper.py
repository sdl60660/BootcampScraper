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

import slack_search_output
from slack_search_output import Slack_Output_Strings
from current_data import attribute_dict


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

def main(search_keys):
    #Translate search terms into scraped category terms

    for i, term in enumerate(search_keys):
        closest_term = return_closest(term.title(), attribute_dict.In_Dict.keys(), 0.92)
        if closest_term != -1:
            search_keys[i] = attribute_dict.In_Dict[closest_term]

    tracking_groups = ['Current Market', 'Potential Market', 'Top Camp', 'Java/.NET', 'Selected Camp']
    tracking_groups_files = find_file('*.json','current_data/tracking_groups')

    text_off = False
    if search_keys[0] == 'filler':
        text_off = True

    if search_keys[-1] == 'Slack':
        search_keys.remove('Slack')
        source = 'Slack'
        #SETS 'SELECTED CAMP' AS DEFAULT TRACKING GROUP FOR ALL SLACK SEARCHES IF NOT MARKED WITH '--all' FLAG
        if all(return_closest(key.title(), tracking_groups, 0.88) == -1 for key in search_keys) and '--all' not in search_keys:
            search_keys.append('Selected Camp')
    else:
        source = 'Terminal'

    #COMMAND LINE OPTION PROCESSING
    or_flag, search_keys = check_flag('--or', search_keys)
    summary_flag, search_keys = check_flag('--summary', search_keys)
    list_flag, search_keys = check_flag('--list', search_keys)
    sort_flag, search_keys = check_flag('--sort', search_keys)
    detail_flag, search_keys = check_flag('--details', search_keys)
    #IMPLEMENT THE FUNCTIONS BELOW
    warnings_flag, search_keys = check_flag('--warnings', search_keys)
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

    result_data, bootcamp_search, tgroup_search = revised_search.main(search_keys)
    if tgroup_search:
        summary_flag = True
        list_flag = True
        sort_flag = True

    if source == 'Terminal':
        if bootcamp_search:
            bootcamps = result_data.bootcamp_data
            print
            for camp in bootcamps:
                print ''.center(40, '*')
                print camp.center(40, '-')
                print ''.center(40, '*')
                pprint(bootcamps[camp])
                print
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
                    if cat in attribute_dict.Out_Dict:
                        print_cat = Out_Dict[cat]
                    else:
                        print_cat = cat
                    print print_cat.title() + ':'
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
        slack_formatted_output = slack_search_output.slack_output(result_data)

        full_outstring = '\n'
        if bootcamp_search:
            full_outstring += slack_formatted_output.bootcamps_out
        elif slack_formatted_output.list_out == -1:
            full_outstring = "\n*Sorry! This search didn't return any results...*\n\n" \
            "This is either a mistake or there are no bootcamps that fit the specified filters.\n" \
            "(Make sure to check the 'Tracking Group' and include --all in your search if you want to search all camps)\n"
        else:
            if not any([list_flag, sort_flag, summary_flag]):
                detail_flag = True
                
            kl_length = len(result_data.key_list.keys())
            filter_length = 0
            for cat in ['Tracking Group', 'Location', 'Technology']:
                if cat in result_data.key_list.keys():
                    filter_length += len(result_data.key_list[cat])
            if kl_length == filter_length:
                list_flag = True

            if detail_flag:
                full_outstring += slack_formatted_output.details_out + '\n\n'
            if list_flag:
                full_outstring += slack_formatted_output.list_out + '\n\n'
            if sort_flag:
                full_outstring += slack_formatted_output.sort_out + '\n\n'
            if summary_flag:
                full_outstring += slack_formatted_output.summary_out + '\n\n'
            if warnings_flag and slack_formatted_output.warnings_out:
                full_outstring += slack_formatted_output.warnings_out + '\n\n'

        if not text_off:
            print full_outstring
        return full_outstring, result_data

if __name__ == '__main__':
    main(sys.argv)