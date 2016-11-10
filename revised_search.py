import utilities
from utilities import return_closest
import json, sys, os, csv
from pprint import pprint
import operator
import os.path

import numpy as np
def mean(numbers):
    return round(float(sum(numbers)) / max(len(numbers), 1), 1)

class Camp_Info:
    def __init__(self, bootcamp_data, category_data, camps, summary=None, camp_list=None, sort=None, key_list=None):
        self.bootcamp_data = bootcamp_data
        self.category_data = category_data
        self.camps = camps
        self.summary = summary if summary is not None else []
        self.camp_list = camp_list if camp_list is not None else []
        self.sort = sort if sort is not None else []
        self.key_list = key_list if key_list is not None else []

def summary_dict(bootcamps, category, parent_cat=None):
    temp_dict = {}
    warning_list = []
    int_cat = False
    for bootcamp in bootcamps:
        camp = bootcamps[bootcamp]
        
        if category not in camp.keys():
            if not parent_cat or parent_cat not in camp.keys() \
            or (camp[parent_cat] and category not in camp[parent_cat].keys()) or not camp[parent_cat]:
                warning_list.append(bootcamp)
                continue

        if parent_cat:
            data = camp[parent_cat][category]
        else:
            data = camp[category]

        if not data or data == '\n' or data == 'N/A' or data == 'No data':
            warning_list.append(bootcamp)
            continue
        try:
            key_check = type(data)
            if key_check == list:
                iter_check = data[0]
        except (KeyError, TypeError):
            continue

        if type(data) is list:
            for item in data:
                if item in temp_dict:
                    temp_dict[item] += 1
                else:
                    temp_dict[item] = 1
        elif type(data) is int or type(data) is float:
            int_cat = True
            if 'List' in temp_dict.keys():
                temp_dict['List'].append(data)
            else:
                temp_dict['List'] = [data]
        elif 'Yes' in data or data.find('available') != -1 \
        or data.find('offer') != -1 or data.find('partnership') != -1:
            if 'Yes' in temp_dict:
                temp_dict['Yes'] += 1
            else:
                temp_dict['Yes'] = 1
        elif 'No' or 'None' in data:
            if 'No' in temp_dict:
                temp_dict['No'] += 1
            else:
                temp_dict['No'] = 1
        else:
            return -1, temp_dict, warning_list

    if int_cat:
        temp_dict['Max'] = max(temp_dict['List'])
        temp_dict['Mean'] = mean(temp_dict['List'])
        temp_dict['Median'] = round((np.median(temp_dict['List'])), 1)
        temp_dict['Min'] = min(temp_dict['List'])
        del temp_dict['List']

    return category, temp_dict, warning_list

def dict_sort(in_dict, full_list=False):
    tuple_list = []

    val_type = None
    for k,v in in_dict.iteritems():
        tuple_list.append([k, v])
        val_type = type(v)

    for i, tup in enumerate(tuple_list):
        try:
            if tup[1] == 'None' or tup[1].find('No') != -1:
                tuple_list[i][1] = 'No'
            elif 'Yes' in tup[1] or tup[1].find('available') != -1 \
            or tup[1].find('offer') != -1 or tup[1].find('partnership') != -1:
                tuple_list[i][1] = 'Yes'
        except AttributeError:
            pass
 
    if val_type == int or val_type == float:
        tuple_list = sorted(tuple_list, key=operator.itemgetter(1), reverse=True)
    elif val_type == list:
        tuple_list = sorted(tuple_list, key=lambda tup: len(tup[1]), reverse=True)
    else:
        tuple_list = sorted(tuple_list, key=operator.itemgetter(1), reverse=False)

    if full_list == False:
        for i, tup in enumerate(tuple_list):
            if val_type == list:
                tuple_list[i][1] = len(tup[1])
    return tuple_list

def sort_dict(bootcamps, category, full_list=False):
    warnings = []
    cat_dict = {}
    secondary_cat = None
    if type(category) is tuple:
        out_category = str(category[1]) + ' (%s)' % category[0]
        secondary_cat = category[1]
        category = category[0]
    else:
        out_category = category
    for bootcamp in bootcamps:
        camp = bootcamps[bootcamp]
        if category not in camp.keys():
            warnings.append(bootcamp)
            continue
        if not camp[category] or camp[category] == '\n':
            warnings.append(bootcamp)
            continue
        try:
            if secondary_cat and not camp[category][secondary_cat]:
                warnings.append(bootcamp)
                continue
        except TypeError:
            warnings.append(bootcamp)
            continue
        try:
            if secondary_cat:
                cat_dict[bootcamp] = camp[category][secondary_cat]
            else:
                cat_dict[bootcamp] = camp[category]
        except (KeyError, TypeError):
            warnings.append(bootcamp)
    st_dict = dict_sort(cat_dict)
    return out_category, st_dict, warnings

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
        try:
            del bootcamps[camp]
        except KeyError:
            pass
    return bootcamps

#1. FIX SUMMARY SO THAT IT ALSO SORTS BY VALUE (MAYBE PRINTS BOTH KEY AND VALUE SORTED)
#2. AND/OR FUNCTIONALITY TO SEARCH END

def main(search_keys):
    import os
    #os.chdir('/Users/samlearner/scrapy_projects/bootcamp_info')

    #GLOBAL LISTS
    tracking_groups = ['Current Market', 'Potential Market', 'Top Camp', 'Java/.NET', 'Selected Camp']
    filter_list = ['Tracking Group', 'Location', 'Technology', 'Category', 'Course Attribute', 'Bootcamp']

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

    #if custom_file == False:
    datafile = 'current_data/output.json'

    #LOAD DATA
    with open(datafile) as json_data:
        bootcamps = json.load(json_data)

    #SORT SEARCH TERMS INTO KEY DICT
    key_dict = {}

    first = True
    for key in key_list:
        if key[1] in key_dict.keys():
            key_dict[key[1]].append(key[0])
        else:
            key_dict[key[1]] = [key[0]]

    # =============WORK ON SECTION BELOW=============
    if 'Meta' in key_dict.keys():
        out_data = bootcamps['meta']
        pprint(out_data)
        return out_data
    
    del bootcamps['meta']

    bootcamp_search = False
    if 'Bootcamp' in key_dict.keys():
        if (len(key_dict['Bootcamp']) + len(key_dict['Tracking Group'])) == (len(search_keys)-1):
            bootcamp_search = True
            del key_dict['Tracking Group']
        del_list = [camp for camp in bootcamps if camp not in key_dict['Bootcamp']]
        for camp in del_list:
            del bootcamps[camp]
        for x in ['Tracking Group', 'Technology', 'Location']:
            key_dict.pop(x, None)
    else:
        #FILTERS: TRACKING GROUPS, LOCATIONS, TECHNOLOGIES
        bootcamps = apply_filter('Tracking Group', 'tracking_groups', bootcamps, key_dict)
        bootcamps = apply_filter('Technology', 'technologies', bootcamps, key_dict)
        bootcamps = apply_filter('Location', 'locations', bootcamps, key_dict)

    tgroup_search = False
    if 'Tracking Group' in key_dict.keys() and len(key_dict['Tracking Group']) == (len(search_keys)-1):
        key_dict['Category'] = ['locations', 'technologies']
        tgroup_search = True

    print 'Filters and Categories in Search: ' + str(key_dict)[1:-1]
            

    # =============WORK ON SECTION ABOVE=============

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
            try:
                if not bootcamps[camp][cat] or bootcamps[camp][cat] == '\n':
                    continue
                else:
                    data.append((cat, bootcamps[camp][cat]))
            except KeyError:
                pass

        #Secondary categories
        for cat in secondary_cats:
            full_cat_title = str(cat[1]) + ' (%s)' % cat[0]
            try:
                data.append((full_cat_title, bootcamps[camp][cat[0]][cat[1]]))
            except (TypeError, KeyError):
                pass
        cat_data_dict[title] = data

    camps = [x for x in bootcamps.keys()]

    summary_item = {}
    summary_item['warning'] = []
    for cat in (select_cats + secondary_cats):
        if type(cat) is tuple:
            category, sum_dict, warning_list = summary_dict(bootcamps, cat[1], cat[0])
            display_cat = '{} ({})'.format(cat[1], cat[0])
        else:
            category, sum_dict, warning_list = summary_dict(bootcamps, cat)
            display_cat = cat
        if category == -1:
            continue
        summary_item[category] = sum_dict
        summary_item['warning'].append((display_cat, warning_list))

    list_item = camps

    sort_item = {}
    sort_item['warning'] = []
    for cat in (select_cats + secondary_cats): #EVENTUALLY NEED TO ADD IN SECONDARY CATS, COURSE ATTRIBUTES AS WELL
        category, st_dict, warning_list = sort_dict(bootcamps, cat)
        sort_item[category] = st_dict
        sort_item['warning'].append((cat, warning_list))
    
    return_info = Camp_Info(bootcamps, cat_data_dict, camps, summary_item, list_item, sort_item, key_dict)

    return return_info, bootcamp_search, tgroup_search

if __name__ == '__main__':
    main(sys.argv)


