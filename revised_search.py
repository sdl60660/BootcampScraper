import utilities
from utilities import return_closest
import json, sys, os, csv, fnmatch
import argparse
from pprint import pprint
import operator
import os.path
import datetime

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

def summary_dict(bootcamps, category):
    temp_dict = {}
    for camp in bootcamps:
        try:
            key_check = type(camp[category])
            if key_check == list:
                iter_check = key_check[0]
        except (KeyError, TypeError):
            continue

        if type(camp[category]) == list:
            for item in camp[category]:
                if item in temp_dict:
                    temp_dict[item] += 1
                else:
                    temp_dict[item] = 1
        elif type(camp[category]) == int:
            if camp[category] in temp_dict:
                temp_dict[camp[category]] += 1
            else:
                temp_dict[camp[category]] = 1
        elif 'Yes' in camp[category] or camp[category].find('available') != -1 \
        or camp[category].find('offer') != -1 or camp[category].find('partnership') != -1:
            if 'Yes' in temp_dict:
                temp_dict['Yes'] += 1
            else:
                temp_dict['Yes'] = 1
        elif 'No' or 'None' in camp[category]:
            if 'No' in temp_dict:
                temp_dict['No'] += 1
            else:
                temp_dict['No'] = 1
        else:
            pass
    return category, temp_dict

def apply_filter(key_filter, data_category, bootcamps, key_dict):
    del_list = []
    if key_filter not in key_dict.keys():
        return bootcamps
    for camp in bootcamps:
        for key in key_dict[key_filter]:
            try:
                if key not in bootcamps[camp][data_category]:
                    del_list.append(camp)
            except (KeyError, TypeError):
                del_list.append(camp)
    for camp in del_list:
        del bootcamps[camp]
    return bootcamps

def parse_categories():
    pass

def main(search_keys):
    import os
    #os.chdir('/Users/samlearner/scrapy_projects/bootcamp_info')
    
    return_data = {}

    #GLOBAL LISTS
    tracking_groups = ['Current Market', 'Potential Market', 'Top Camp', 'Java/.NET', 'Selected Camp']
    tracking_groups_files = find_file('*.json','current_data/tracking_groups')
    filter_list = ['Tracking Group', 'Location', 'Technology', 'Category', 'Course Attribute', 'Bootcamp']
    warning_list = []

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

    #OPEN SEARCH TERM FILE FROM CURRENT DATA AND LOAD CSV DATA INTO SEARCH LIST
    #IN THE FORM OF "(term, type)"
    search_list = []
    cat_list = []
    search_term_file = 'current_data/search_terms.csv'
    with open(search_term_file, 'r') as term_csv:
        search_terms = csv.reader(term_csv)
        for row in search_terms:
            search_list.append((row[0], row[1]))
            if row[1] == 'Category':
                cat_list.append(row[0])

    if len(search_keys) == 2 and search_keys[1] == 'terms':
        pprint(search_list)
        sys.exit()

    #MATCH ALL OF THE QUERIES WITH SEARCH TERMS TO GET A LIST OF KEYS
    key_list = []
    for i in range(1, len(search_keys)):
        key = return_closest(search_keys[i], search_list, 0.7)
        key_list.append(key)

    #IF NO SEARCH TERMS WENT THROUGH, EXIT THE FUNCITON INSTEAD OF PRINTING ALL
    key_list = [x for x in key_list if x != -1]
    if len(key_list) == 0:
        print 'No keys were entered or none of the entered keys were found. Aborting...'
        print
        sys.exit()

    if custom_file == False:
        datafile = 'current_data/output.json'

    #SORT SEARCH TERMS INTO KEY DICT
    tracking_list = []
    key_dict = {}

    first = True
    for key in key_list:
        if key[1] in key_dict.keys():
            key_dict[key[1]].append(key[0])
        else:
            key_dict[key[1]] = [key[0]]

    print key_dict

    #LOAD DATA
    with open(datafile) as json_data:
        bootcamps = json.load(json_data)

    if 'Meta' in key_dict.keys():
        out_data = bootcamps['meta']
        return out_data

    if 'Bootcamp' in key_dict.keys():
        out_data = []
        for bootcamp in key_dict['Bootcamp']:
            out_data.append(bootcamps[bootcamp])
        for b in out_data:
            pprint(b)
        return out_data

    #FILTERS: TRACKING GROUPS, LOCATIONS, TECHNOLOGIES
    bootcamps = apply_filter('Tracking Group', 'tracking_groups', bootcamps, key_dict)
    bootcamps = apply_filter('Technology', 'technologies', bootcamps, key_dict)
    bootcamps = apply_filter('Location', 'locations', bootcamps, key_dict)

    if list_flag == True and set(['Tracking Group', 'Technology', 'Location']).issuperset(key_dict.keys()):
        camps = [x for x in bootcamps.keys()]
        title_string = '\n===============================================================================================\n\n' \
        'LIST: The following bootcamps fit the inputed tracking group, location, and technology filters (Total Camps in Query: ' + str(len(camps)) + ')\n\n'
        return_dict['list'] = (title_string, camps)
        return title_string, camps

    """if sort_flag == True:
        title_string = '===============================================================================================\n\n' \
        'SORT: Sorted list of camps by specified categories\n\n'"""

    """Filter selected categories out of keys and secondary keys. Courses will stay in as long as there's a course category
    in the key dict"""
    try:
        select_cats = [x for x in key_dict['Category']]
    except KeyError:
        select_cats = []

    if 'Course Attribute' in key_dict.keys():
        course_categories = [x for x in key_dict['Course Attribute']]
        select_cats.append('courses_cat')

    secondary_cats = []

    for cat_key in key_dict.keys():
        if cat_key in cat_list:
            for sub_cat in key_dict[cat_key]:
                secondary_cats.append((cat_key, sub_cat))

    cat_data_dict = {}
    for camp in bootcamps:
        title = camp #.center(30)
        #print '----------------------'
        data = []

        #Course categories
        if 'courses_cat' in select_cats:
            course_dict = {}
            select_cats.remove('courses_cat')
            for course in bootcamps[camp]['courses']:
                course_cat = {}
                for item in key_dict['Course Attribute']:
                    try:
                        course_cat[item] = bootcamps[camp]['courses'][course][item]
                    except KeyError:
                        pass
                course_dict[course] = course_cat
            data.append(('courses', course_dict))

        #Regular categories
        for cat in select_cats:
            data.append((cat, bootcamps[camp][cat]))

        #Secondary categories
        for cat in secondary_cats:
            full_cat_title = str(cat[1]) + ' (%s)' % cat[0]
            data.append((full_cat_title, bootcamps[camp][cat[0]][cat[1]]))
            #print cat.title() + ': ' + str(bootcamps[camp][cat])
        #print
        cat_data_dict[title] = data
    #pprint(cat_data_dict)
    return_data['category_data'] = cat_data_dict
    return

    #bootcamps = filter(key in bootcamps[camp]['tracking_group'], bootcamps)

if __name__ == '__main__':
    main(sys.argv)


