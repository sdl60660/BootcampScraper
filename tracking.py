import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from utilities import return_closest, dict_print, is_number

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
            return json.load(open(generate_filename(target_date, tracking_group), 'rb'))
        except IndexError:
            try:
                target_date = date.fromordinal(today_ordinal - ordinal_back - 1)
                return json.load(open(generate_filename(target_date, tracking_group), 'rb'))
            except IndexError:
                target_date = date.fromordinal(today_ordinal - ordinal_back - 2)
    elif target_date.weekday() == 5:
        try:
            return json.load(open(generate_filename(target_date, tracking_group), 'rb'))
        except IndexError:
            target_date = date.fromordinal(today_ordinal - ordinal_back - 1)
    try:
        filename = generate_filename(target_date, tracking_group)
    except IndexError:
        #print target_date, tracking_group
        #print 'Sorry! No file found for that date. Please enter a new one.'
        raise NameError('Sorry! No file found for that date. Please enter a new one.')
    return json.load(open(filename, 'rb'))


today = date.today()
today_ordinal = today.toordinal()

#OPEN CURRENT FILE
if os.getcwd() == '/Users/samlearner/scrapy_projects/bootcamp_info/slackbot':
    os.chdir('..')
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
        try:
            if camp[category] == None:
                    continue
        except KeyError:
            continue
        if tracking_group == 'ALL':
            pass
        elif tracking_group not in camp['tracking_groups']:
            continue

        for item in camp[category]:
            try:
                if item not in old_data[x][category]:
                    new_points.append((item, x, 'Addition'))
            except (KeyError, TypeError):
                new_points.append((item, x, 'Addition'))
        
        try:
            for item in old_data[x][category]:
                if item not in camp[category]:
                    new_points.append((item, x, 'Subtraction'))
        except (KeyError, TypeError):
            pass
    return new_points


def tracking_group_stats(days_back, tracking_group='ALL', highlight_length=3):
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
    diff_arrays = []

    for x in current_meta:
        cat = current_meta[x]
        if type(cat) is list:
            for item in cat:
                if item not in old_meta[x]:
                    print str(x).title() + ': ' + str(item)
        elif type(cat) is dict:
            max_diff = [(None, 0) for j in range(highlight_length)]
            print_array = []
            for key, value in cat.iteritems():
                try:
                    old_val = old_meta[x][key]
                except KeyError:
                    old_val = 0
                if value != old_val:
                    diff = value - old_val
                    max_diff = sorted(max_diff, key=lambda x: abs(x[1]), reverse=True)
                    for i, item in enumerate(max_diff):
                        if abs(diff) > abs(item[1]):
                            max_diff.insert(i, (key, diff))
                            max_diff = max_diff[:-1]
                            break
                    out_str = str(key) + ': ' + str(value) + ' (%+d)' % diff
                    print_array.append((out_str, value))
            print_array = sorted(print_array, key=lambda y: y[1], reverse=True)
            print_array = [item[0] for item in print_array]
            print_arrays.append((print_array, x))
            diff_arrays.append(max_diff)

    return print_arrays, diff_arrays

def plot_changes(days_back, category, start_days_back=0, current_status=False, tracking_group=None, max_items=10,
    percentage=True, start_item=0, show_legend=True, interval=1, active_only=True, show_plot=True, save_plot=True,
    slack_post=False):
    
    #Import modules
    import matplotlib.pyplot as plt
    import datetime
    from datetime import date
    import math
    from bootcamp_info.helper_functions.json_merge import create_meta_dict
    from utilities import is_number
    import numpy as np

    def filter_data(data, list_of_camps):
        temp_dict = {}
        for k,v in data.iteritems():
            if k == 'meta':
                date_time = datetime.datetime.strptime(str(v['Date/Time']), '%Y-%m-%d %H:%M:%S')
            if k in list_of_camps:
                temp_dict[k] = v
        del temp_dict['meta']
        meta_entry = create_meta_dict(date_time, temp_dict)
        temp_dict['meta'] = meta_entry
        return temp_dict

    def int_check(category, data, child_cat=None):
        out_data = []
        out_camps = []
        for camp in data.keys():
            if category in data[camp].keys():
                item = data[camp][category]

                if child_cat and data[camp][category]:
                    if child_cat in data[camp][category].keys():
                        item = data[camp][category][child_cat]
                    else:
                        course_att_list = [data[camp][category][course][child_cat] for course in data[camp][category].keys() \
                        if child_cat in data[camp][category][course].keys() and data[camp][category][course][child_cat]]
                        
                        if len(course_att_list) > 0:
                            item = int(max(course_att_list))
                        else:
                            item = 'N/A'

                if type(item) is int or type(item) is float:
                    out_data.append(item)
                    out_camps.append(camp)
        return out_data, out_camps


    #------------------------------------------------------------------------------------------------


    #Set today's date for reference
    today = date.today()
    today_ordinal = today.toordinal()

    #Load date data for "today". If start_days_back == 0, this won't actually be today, but
    #will the data for the last data point
    if start_days_back == 0:
        today_data = bootcamps
    else:
        today_data = load_date_data(today_ordinal, start_days_back)
        today_ordinal = today_ordinal - start_days_back

    filtered_camps = [camp for camp in today_data.keys()]
    if tracking_group and tracking_group != 'ALL':
        if type(tracking_group) is str:
            tracking_group = return_closest(tracking_group, tracking_groups, 0.7)
            filtered_camps = [camp for camp in today_data.keys() if camp != 'meta' and tracking_group in today_data[camp]['tracking_groups']]
            
        elif type(tracking_group) is list:
            filtered_camps = [return_closest(camp, today_data.keys(), 0.93) for camp in tracking_group if return_closest(camp, today_data.keys(), 0.93) != -1]
        filtered_camps.append('meta')
    today_data = filter_data(today_data, filtered_camps)

    non_meta_cat = False
    child_cat = None
    if type(category) is tuple:
        child_cat = category[0]
        category = category[1]
        if category == 'Course Attribute':
            category = 'courses'

    parent_cat = None
    out_data, out_camps = int_check(category, today_data, child_cat)
    if len(out_data) > 0:
        if child_cat:
            today_data['meta'][child_cat] = out_data
            parent_cat = category
            category = child_cat
        else:
            today_data['meta'][category] = out_data
        non_meta_cat = True


    #------------------------------------------------------------------------------------------------


    #Initialize x-axis values and labels(dates) with the values for today or 'today'
    date_labels = [str(datetime.date.fromordinal(today_ordinal))[5:]]
    x_axis = [int(today_data['meta']['Days Out'])]

    #Find closest meta category for input to allow for slight spelling or syntax mistakes with
    #input, such as inputing 'Location' instead of 'locations'
    meta_cat_list = [x for x in today_data['meta'].keys()]
    category = return_closest(category, meta_cat_list, 0.7)

    #If all of the items in dataset aren't either a dict or a tracking category,
    #there's going to be an issue, so return with error message
    
    if (category == -1) or (type(today_data['meta'][category]) != dict and category not in tracking_groups and not non_meta_cat):
        error_string = 'The selected category cannot be plotted! Please use another category.'
        print error_string
        return error_string, None

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
    #==========LOAD DATESETS==========
    for day in range(1, (days_back+1), interval):
        try:
            day_data = filter_data(load_date_data(today_ordinal, day), filtered_camps)

            if child_cat:
                child_cat = category
                category = parent_cat
            out_data, out_camps = int_check(category, day_data, child_cat)
            if len(out_data) > 0:
                if child_cat:
                    day_data['meta'][child_cat] = out_data
                    parent_cat = category
                    category = child_cat
                else:
                    day_data['meta'][category] = out_data
                    parent_cat = None
            meta_data = day_data['meta']

            if meta_data['Active'] == False and active_only == True:
                raise NameError('Non-active date for datafile')
            
            if subs == True:
                datasets.append([meta_data[s_cat] for s_cat in subcats])
            else:
                datasets.append(meta_data[category])

            totals.append(meta_data['Number of Entries'])
        #If there's no corresponding dataset for a date, mark it with 'NO DATA'
        except (KeyError, NameError, AttributeError):
            datasets.append('NO DATA')
            totals.append('NO DATA')

        date_labels.append(str(meta_data['Date/Time'])[5:10])
        x_axis.append(int(meta_data['Days Out']))
    date_labels = date_labels[::-1]
    x_axis = x_axis[::-1]

    data_list = []


    #==========PROCESS DATA INTO DATASETS==========

    for i, x in enumerate(datasets):
        if type(x) is list and len(x) == 1 and type(x[0]) is list:
            datasets[i] = x[0]
    
    if type(datasets[0]) is list and type(datasets[0][0]) is not int and type(datasets[0][0]) is not float:
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
            #print num_list
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
        if type(max_items) is int:
            item_list = [x[0] for x in temp_list[start_item:(start_item+max_items)]]
        elif type(max_items) is list:
            cat_list = [x[0] for x in temp_list]
            max_items = [return_closest(x, cat_list, 0.85) for x in max_items if return_closest(x, cat_list, 0.85) != -1]
            item_list = [x[0] for x in temp_list if x[0] in max_items]
        num_items = len(item_list)

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
                    try:
                        if percentage == True:
                            num_list.append(100*s[item]/float(totals[i]))
                        else:
                            num_list.append(s[item])
                    except KeyError:
                        num_list.append(None)
                else:
                    num_list.append(None)
            num_list = num_list[::-1]
            data_list.append((num_list, item))

    else:
        for i, s in enumerate(datasets):
            if s == 'NO DATA':
                data_list.append(None)
            elif all([is_number(x) or type(x) is int for x in s]):
                data_list.append(s)
            else:
                data_list.append(None)
        datasets = data_list[::-1]

    #-----------------PLOT THE DATA-----------------#

    #Set up plot
    fig = plt.figure()
    ax = plt.subplot(111)

    #Set correct category labels
    os.chdir('/Users/samlearner/scrapy_projects/bootcamp_info')
    from current_data.attribute_dict import In_Dict, Out_Dict
    if category in Out_Dict.keys():
        cat_label = Out_Dict[category]
    else:
        cat_label = ' '.join(category.split('_')).title()
    if parent_cat:
        cat_label += ' ({})'.format(parent_cat.title())

    if type(datasets[-1]) is list and is_number(datasets[-1][-1]):
        if current_status:
            plt.xlim([0,max(datasets[-1])])
            plt.xlabel(cat_label)
            plt.ylabel('# of Camps')
            title = "Distribution of Bootcamps' " + str(cat_label) + ' (as of {})'.format(str(date_labels[-1]))

            num_bins = max([int(max(datasets[-1]) - min(datasets[-1])), len(set(datasets[-1]))])
            
            if num_bins > 150:
                from math import ceil
                max_bin = np.log10(max(datasets[-1]))
                num_bins = np.logspace(0.1, max_bin, 50)

                plt.xlim([1,10*ceil(max_bin)])
                plt.xscale('log')

                ticks = [int(x) for x in np.logspace(1,ceil(max_bin), ceil(max_bin))]
                tick_labels = [str(x) for x in ticks]
                plt.xticks(ticks, tick_labels)

            n, bins, patches = ax.hist(datasets[-1], bins=num_bins, facecolor=np.random.rand(3,1), alpha=0.6)

        else:
            def mean(numbers):
                return round(float(sum(numbers)) / max(len(numbers), 1), 1)
            items = ['Max', 'Min', 'Mean', 'Median']
            max_list = []
            min_list = []
            mean_list = []
            median_list = []

            for dset in datasets:
                if dset:
                    max_list.append(max(dset))
                    min_list.append(min(dset))
                    mean_list.append(mean(dset))
                    median_list.append(np.median(dset))
                else:
                    max_list.append(None)
                    min_list.append(None)
                    mean_list.append(None)
                    median_list.append(None)
            plots = [max_list, min_list, mean_list, median_list]
            for i, ilist in enumerate(plots):
                ax.plot(x_axis, ilist, label=items[i])

            plt.ylim([0,int(max(max_list) + max(max_list)/10)])

            num_items = 8

    elif current_status:
        bar_plot = []
        bar_labels = []
        for a, array in enumerate(data_list):
            bar_plot.append(array[0][-1])
            bar_labels.append(array[1])

        x_locations = np.arange(len(bar_plot))
        tick_locations = [(x + 0.25) for x in x_locations]

        #my_colors = 'rgbkymc'
        my_colors = []
        for x in range(len(bar_plot)):
            my_colors.append(np.random.rand(3,1))
        ax.bar(x_locations, bar_plot, color=my_colors, zorder=3)

        ax.set_xlabel(category.title())
        y_label = 'Prevelance Among Bootcamp Group (%s)' % ('Total' if percentage==False else '%')
        ax.set_ylabel(y_label)

        ax.grid(zorder=0)
        fsize = 12/((num_items/2)**0.4)
        if fsize < 8:
            fsize = 8
        if num_items > 60:
            fsize = 5
        rot = 104-(fsize*6)
        if num_items > 20:
            rot = 90
        if rot < 40:
            tick_locations = [loc + 0.125 for loc in tick_locations]
        plt.xticks(tick_locations, bar_labels, rotation=rot, fontsize=fsize)
        
        title = 'Showing Information on ' + cat_label + ' (as of {})'.format(str(date_labels[-1]))
    
    else:
        #Plot a line for each of the item lists in data_list
        for i, ilist in enumerate(data_list):
            print ilist
            print x_axis
            ax.plot(x_axis, ilist[0], label=ilist[1])
        
        #Set axis labels, adjust based on whether the setting was for raw number or percentage
        if percentage == False:
            plt.ylabel('# of Bootcamps', fontsize='medium')
        else:
            plt.ylabel('% of Bootcamps', fontsize='medium')
            plt.ylim([0,105])
        plt.xlabel('Date', fontsize='medium')
        plt.ylim(ymin=0)

    if not current_status:
        #Put date labels on the x_axis for each dataset's meta date field
        plt.xticks(x_axis, date_labels, fontsize=7, rotation=60)

        #Arrange, position, format the legend if show_legend is True
        if show_legend == True:
            columns = int(math.floor(num_items/2))
            if columns > 6:
                columns = 6
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.075),
                fancybox=True, shadow=True, ncol=columns)
            
        #Set plot title
        if tracking_group == None:
            tgroup_label = ''
        elif len(str(tracking_group)) < 100:
            tgroup_label = ' (Tracking Group: ' + str(tracking_group) + ')'
        else:
            tgroup_label = ' (Tracking Group: Previous Result)'
        
        title = 'Showing Information on ' + cat_label + ' for: ' \
         + date_labels[0] + ' to ' + date_labels[-1] + '\n' + tgroup_label
    
    fig.suptitle(title, fontsize=13)
    title = ''.join(title.split('\n'))
    if title.startswith('Distribution'):
        plot_title = title
    else:
        plot_title = title[(title.find('Information on ') + 15):]
    if save_plot == True:
        if slack_post:
            subfolder = 'slack_requests'
        else:
            subfolder = 'trend_charts'
        
        if '/' in plot_title:
            temp_plot_title = '-'.join(plot_title.split('/'))
            plot_file_name = 'old_data/' + subfolder + '/' + temp_plot_title
        else:
            plot_file_name = 'old_data/' + subfolder + '/' + plot_title
        plt.savefig(plot_file_name, bbox_inches='tight')
    else:
        plot_file_name = 'No plot saved.'

    #Show plot
    if show_plot == True:
        plt.show()
    
    return plot_file_name, plot_title

#PLOTS SPECIFIED BOOTCAMPS FOR SPECIFIED CATEGORIES (I.E. NUM_LOCATIONS FOR SPECIFIED BOOTCAMPS OVER TIME)
def plot_bootcamp_info():
    pass

#TRACK WHEN NEW BOOTCAMPS ARE ADDED TO THE DATA SET
def new_bootcamps(days_back, start_date=0):
    today_ordinal = date.today().toordinal()

    if start_date == 0:
        with open('current_data/output.json', 'rb') as current_data:
            bootcamps = json.load(current_data)
        reference = load_date_data(today_ordinal, days_back)
    else:
        bootcamps = load_date_data(today_ordinal, start_date)
        start_ordinal = today_ordinal - start_date
        reference = load_date_data(start_ordinal, days_back)
    
    new_camps = [x for x in bootcamps if x not in reference]
    for x, camp in enumerate(new_camps):
        new_camps[x] = (camp, bootcamps[camp]['locations'])

    return new_camps


