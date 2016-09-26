import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from utilities import return_closest, dict_print

from pprint import pprint
import numpy as np
import os, fnmatch
import sys

import json
import jsonmerge

import filecmp

tracking_groups = ['Java/.NET', 'Potential Market', 'Current Market', 'Top Camp', 'Selected Camp']
tracking_group_files = ['current_markets.json', 'java_and_NET.json', 'potential_markets.json', 'selected_camps.json', 'top_camps.json']

def find_file(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

def generate_filename(date, tracking_group=None):
    date_input = str(date) + '.*'
    if tracking_group:
        file_stub = return_closest(tracking_group, tracking_group_files, 0.4)
        date_input += file_stub
        filename = find_file(date_input, 'old_data/tracking_groups/')[-1]
    else:
        filename = find_file(date_input,'old_data/full_outputs/')[-1]
    return filename

def load_date_data(today_ordinal, ordinal_back, tracking_group=None):
    target_date = date.fromordinal(today_ordinal - ordinal_back)
    
    if target_date.weekday() == 6:
        try:
            filename = generate_filename(target_date, tracking_group)
            return json.load(open(filename, 'rb'))
        except IndexError:
            target_date = date.fromordinal(today_ordinal - ordinal_back - 2)
    elif target_date.weekday() == 5:
        try:
            filename = generate_filename(target_date, tracking_group)
            return json.load(open(filename, 'rb'))
        except IndexError:
            target_date = date.fromordinal(today_ordinal - ordinal_back - 1)
    try:
        filename = generate_filename(target_date, tracking_group)
    except IndexError:
        #print 'Sorry! No file found for that date. Please enter a new one.'
        raise NameError('Sorry! No file found for that date. Please enter a new one.')
    return json.load(open(filename, 'rb'))


today = date.today()
today_ordinal = today.toordinal()

#OPEN CURRENT FILE
with open('current_data/output.json', 'rb') as current_data:
    bootcamps = json.load(current_data)


def tracked_camp_changes(days_back, category, tracking_group='ALL'):
    #today = date.today()
    #today_ordinal = today.toordinal()

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
            try:
                if item not in old_data[x][category]:
                    new_points.append((item, x, 'Addition'))
            except KeyError:
                new_points.append((item, x, 'Addition'))
        
        try:
            for item in old_data[x][category]:
                if item not in camp[category]:
                    new_points.append((item, x, 'Subtraction'))
        except KeyError:
            pass
    return new_points


def tracking_group_stats(days_back, tracking_group='ALL'):
    with open('current_data/output.json', 'rb') as current_data:
        bootcamps = json.load(current_data)
    old_data = load_date_data(today_ordinal, days_back)

    if tracking_group != 'ALL':
        file_stub = return_closest(tracking_group, tracking_group_files, 0.5)
        filename = 'current_data/tracking_groups/' + file_stub
        with open(filename, 'rb') as current_data:
            bootcamps = json.load(current_data)
        old_data = load_date_data(today_ordinal, days_back, tracking_group)

    current_meta = bootcamps['meta']
    old_meta = old_data['meta']

    print_arrays = []

    for x in current_meta:
        cat = current_meta[x]
        if type(cat) is list:
            for item in cat:
                if item not in old_meta[x]:
                    print str(x).title() + ': ' + str(item)
        elif type(cat) is dict:
            print_array = []
            for key, value in cat.iteritems():
                try:
                    old_val = old_meta[x][key]
                except KeyError:
                    old_val = 0
                if value != old_val:
                    diff = value - old_val
                    out_str = str(key) + ': ' + str(value) + ' (%+d)' % diff
                    print_array.append((out_str, value))
            print_array = sorted(print_array, key=lambda x: x[1], reverse=True)
            print_array = [item[0] for item in print_array]
            """if len(print_array) > 0:
                print
                print str(x).upper()
            for change in print_array:
                pprint(change, indent=4)"""
            print_arrays.append((print_array, x))
                    
    return print_arrays

def plot_changes(days_back, category, start_days_back=0, tracking_group=None, max_items=10,
    percentage=False, start_item=0, show_legend=True, interval=1, active_only=True, show_plot=True, save_plot=True):
    
    #Import modules
    import matplotlib.pyplot as plt
    import heapq
    from datetime import date
    import math

    #Set today's date for reference
    today = date.today()
    today_ordinal = today.toordinal()

    #Load date data for "today". If start_days_back == 0, this won't actually be today, but
    #will the data for the last data point
    if start_days_back == 0 and tracking_group==None:
        today_data = bootcamps
    else:
        today_data = load_date_data(today_ordinal, start_days_back, tracking_group)
        today_ordinal = today_ordinal - start_days_back

    #Initialize x-axis values and labels(dates) with the values for today or 'today'
    date_labels = [str(datetime.date.fromordinal(today_ordinal))[5:]]
    x_axis = [int(today_data['meta']['Days Out'])]

    #Find closest meta category for input to allow for slight spelling or syntax mistakes with
    #input, such as inputing 'Location' instead of 'locations'
    meta_cat_list = [x for x in today_data['meta'].keys()]
    category = return_closest(category, meta_cat_list, 0.7)

    #If all of the items in dataset aren't either a dict or a tracking category,
    #there's going to be an issue, so return with error message
    if type(today_data['meta'][category]) != dict and category not in tracking_groups:
        raise ValueError('The selected category cannot be plotted! Please enter another category.')

    #Initialize the list of datasets with the dataset from today or 'today', as well as
    #the list that holds total # of bootcamps in each dataset
    datasets = [today_data['meta'][category]]
    totals = [today_data['meta']['Number of Entries']]

    subs = False
    if type(datasets[0]) is list:
        datasets = []
        if category == 'Current Market':
            subcats = ['Current Market', 'Cleveland', 'Columbus']
        elif category == 'Potential Market':
            subcats = ['Potential Market', 'Pittsburgh', 'Detroit', 'Cincinnati', 'Buffalo', 'Toronto']
        else:
            subcats = [category]
        datasets.append([today_data['meta'][s_cat] for s_cat in subcats])
        subs = True
    else:
        datasets = [today_data['meta'][category]]

    #Fill these x-axis, label, dataset, total bootcamp lists with data from appropriately
    #dated dataset meta data
    for day in range(1, (days_back+1), interval):
        try:
            meta_data = load_date_data(today_ordinal, day, tracking_group)['meta']
            if meta_data['Active'] == False and active_only == True:
                raise NameError('Non-active date for datafile')
            if subs == True:
                datasets.append([meta_data[s_cat] for s_cat in subcats])
            else:
                datasets.append(meta_data[category])
            totals.append(meta_data['Number of Entries'])
        #If there's no corresponding dataset for a date, mark it with 'NO DATA'
        except (KeyError, NameError):
            datasets.append('NO DATA')
            totals.append('NO DATA')
        date_labels.append(str(meta_data['Date/Time'])[5:10])
        x_axis.append(int(meta_data['Days Out']))
    date_labels = date_labels[::-1]
    x_axis = x_axis[::-1]

    data_list = []

    #**************HERE**************#
    #This function should combine what's in the list and dict options as much as possible
    #so that there aren't so many overlapping/wasted lines
    def fill_data_list():
        pass

    if type(datasets[0]) is list:
        for x, item in enumerate(subcats):
            num_list = []
            for i, s in enumerate(datasets):
                if s != 'NO DATA':
                    if percentage == True:
                        num_list.append(100*len(s[x])/float(totals[i]))
                    else:
                        num_list.append(len(s[x]))
                else:
                    num_list.append(None)
            num_list = num_list[::-1]
            print num_list
            data_list.append((num_list, item))



    elif type(datasets[0]) is dict:
        #Use the most recent dataset to determine the category items in the range start_item:max_items
        #For example, if start_item=10 and max_items=3, it might fill item list with Java, AngularJS, .NET
        #If those were the 10th through 12th most popular technologies in the most current dataset
        current = datasets[0]
        temp_list = []
        for k, v in current.iteritems():
            temp_list.append((k, v))
        temp_list = sorted(temp_list, key=lambda x: x[1], reverse=True)
        item_list = [x[0] for x in temp_list[start_item:(start_item+max_items)]]

        #Fill data_list with a set of lists, one for each of category items identified above
        #Each of these category item lists contains values for that item for each of the required dates
        for item in item_list:
            num_list = []
            for i, s in enumerate(datasets):
                #If a date did not have a corresponding dataset, it was marked 'NO DATA' above,
                #Fill these with None values
                #For everything else, fill with the appropriate value or, if percentage is True,
                #Fill with the percent of total bootcamps in the set that have this category item
                if s != 'NO DATA':
                    if percentage == True:
                        num_list.append(100*s[item]/float(totals[i]))
                    else:
                        num_list.append(s[item])
                else:
                    num_list.append(None)
            num_list = num_list[::-1]
            data_list.append((num_list, item))

    #-----------------PLOT THE DATA-----------------#

    #Set up plot
    fig = plt.figure()
    ax = plt.subplot(111)

    #Plot a line for each of the item lists in data_list
    for i, ilist in enumerate(data_list):
        print ilist
        print x_axis
        ax.plot(x_axis, ilist[0], label=ilist[1])

    #Arrange, position, format the legend if show_legend is True
    if show_legend == True:
        columns = int(math.floor(max_items/2))
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
             box.width, box.height * 0.9])
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.075),
            fancybox=True, shadow=True, ncol=columns)
    
    #Put date labels on the x_axis for each dataset's meta date field
    plt.xticks(x_axis, date_labels, fontsize=7)
    
    #Set axis labels, adjust based on whether the setting was for raw number or percentage
    if percentage == False:
        plt.ylabel('# of Bootcamps', fontsize='medium')
    else:
        plt.ylabel('% of Bootcamps', fontsize='medium')
    plt.xlabel('Date', fontsize='medium')
    plt.ylim(ymin=0)
    
    #Set plot title
    if tracking_group == None:
        tgroup_label = ''
    else:
        tgroup_label = ' (Tracking Group: ' + str(tracking_group) + ')'
    
    title = 'Showing Information on ' + str(category).title() + ' for: ' \
     + date_labels[0] + ' to ' + date_labels[-1] + tgroup_label
    fig.suptitle(title, fontsize=13)

    if save_plot == True:
        plot_file_name = 'old_data/trend_charts/' + title[(title.find('Information on ') + 15):]
        plt.savefig(plot_file_name, bbox_inches='tight')

    #Show plot
    if show_plot == True:
        plt.show()

    return

#PLOTS IN BAR OR PIE CHART THE MOST RECENT BREAKDOWN FOR A CATEGORY
def plot_category():
    pass

#PLOTS SPECIFIED BOOTCAMPS FOR SPECIFIED CATEGORIES (I.E. NUM_LOCATIONS FOR SPECIFIED BOOTCAMPS OVER TIME)
def plot_bootcamp_info():
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






