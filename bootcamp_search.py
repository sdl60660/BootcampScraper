import json
import csv
import sys
from pprint import pprint
import operator
import os.path
import os, fnmatch
import datetime

from difflib import SequenceMatcher

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

def dict_print(in_dict, title):
    print title.title() + ':'
    tuple_list = []

    for k,v in in_dict.iteritems():
        tuple_list.append((k, v))
        val_type = type(v)
 
    if val_type == int or val_type == float:
        tuple_list = sorted(tuple_list, key=operator.itemgetter(1), reverse=True)
    elif val_type == list:
        tuple_list = sorted(tuple_list, key=lambda tup: len(tup[1]), reverse=True)
    else:
        tuple_list = sorted(tuple_list, key=operator.itemgetter(1), reverse=False)
    
    for tup in tuple_list:
        if val_type == list:
            print_string = unicode(tup[0])+ ': ' + unicode(len(tup[1]))
        else:
            print_string = unicode(tup[0])+ ': ' + unicode(tup[1])
        pprint(print_string, indent=4)
    print
    return

def summary_print(bootcamps, categories, filtered_camps):
    print '==============================================================================================='
    print
    print 'SUMMARY: Breakdown of specified categories (Total Camps in Query: ' + str(len(filtered_camps)) + ')'
    print
    for cat in categories:
        temp_dict = {}
        for camp in filtered_camps:
            camp = bootcamps[camp]
            try:
                if type(camp[cat]) == list:
                    for item in camp[cat]:
                        if item in temp_dict:
                            temp_dict[item] += 1
                        else:
                            temp_dict[item] = 1
                #NEED TO USE BINS HERE, MIGHT BE WORTH FIGURING OUT LATER
                elif type(camp[cat]) == int:
                    if camp[cat] in temp_dict:
                        temp_dict[camp[cat]] += 1
                    else:
                        temp_dict[camp[cat]] = 1
                elif 'Yes' in camp[cat] or camp[cat].find('available') != -1 or camp[cat].find('offer') != -1 or camp[cat].find('partnership') != -1:
                    if 'Yes' in temp_dict:
                        temp_dict['Yes'] += 1
                    else:
                        temp_dict['Yes'] = 1
                elif 'No' or 'None' in camp[cat]:
                    if 'No' in temp_dict:
                        temp_dict['No'] += 1
                    else:
                        temp_dict['No'] = 1
                else:
                    pass
            except (KeyError, TypeError):
                pass
        dict_print(temp_dict, cat)
    return

def sort_print(bootcamps, categories, filtered_camps):
    print '==============================================================================================='
    print
    print 'SORT: Sorted list of camps by specified categories'
    print
    camp_dict = {}
    for camp in filtered_camps:
        camp_dict[camp] = bootcamps[camp]
    for cat in categories:
        cat_dict = {}
        for camp in camp_dict:
            try:
                cat_dict[camp] = camp_dict[camp][cat]
            except (KeyError, TypeError):
                continue
        dict_print(cat_dict, cat)
        print

    return

def return_closest(query, search_set, threshold):
    closest = (None, 0.0)
    for term in search_set:
        if type(term) == tuple:
            match = SequenceMatcher(None, query.lower(), term[0].lower()).ratio()
        else:
            match = SequenceMatcher(None, query.lower(), term.lower()).ratio()
        if match > closest[1]:
            closest = (term, match)
    if closest[1] < threshold:
        print
        print 'Sorry! Your search term "' + str(query) + '" did not return a close enough match with any search terms. It may not be in the dataset.'
        print
        return -1
    #print closest
    return closest[0]

def category_print(info, cat, parent_cat=None):
    if parent_cat:
        title = unicode(cat).title() + ' (' + unicode(parent_cat).title() + ')'
    else:
        title = unicode(cat).title()

    if type(info[cat]) is list:
        print title + ':'
        pprint(info[cat], indent=4)
    elif type(info[cat]) is dict:
        print title + ':'
        if cat == 'courses':
            for key in info[cat].keys():
                print '    ' + str(key)
                pprint(info[cat][key], indent=8)
                print
        else:
            sort_dict = []
            for key in info[cat].keys():
                temp_string = '    ' + unicode(key) + ': ' + unicode(info[cat][key])
                sort_dict.append(temp_string)
                sort_dict = sorted(sort_dict, key=lambda x: (len(x), x))
            for item in sort_dict:
                print item
    else:
        if info[cat] == None:
            print title + ': N/A'
        else:
            print title + ': ' + unicode(info[cat])
    return

def info_print(title, info, categories=None, course_categories=None, secondary_categories=None):
    empty = True
    if categories == None and course_categories == None and secondary_categories == None:
        empty = False

    if categories:
        for cat in categories:
            try:
                x = info[cat]
                empty = False
            except KeyError:
                pass

    if course_categories:
        for cat in course_categories:
            try:
                for c in info['courses']:
                    try:
                        x = info['courses'][c][cat]
                        empty = False
                    except KeyError:
                        pass
            except KeyError:
                pass


    if secondary_categories:
        for cat in secondary_categories:
            try:
                x = info[cat[0]][cat[1]]
                empty = False
            except KeyError:
                pass

    if empty == True:
        warning_list.append(title)
        return

    string = "INFORMATION FOR BOOTCAMP: " + str(title)
    print
    print "======================================================================"
    print string.center(70)
    print "======================================================================"
    print
    if categories == None and course_categories == None and secondary_categories == None:
        pprint(info)
    
    if categories != None:
        for cat in categories:
            try:
                category_print(info, cat)
                print
            except KeyError:
                pass

    if secondary_categories != None:
        for tup in secondary_categories:
            try:
                if info[tup[0]] != 'N/A' and info[tup[0]] != None:
                    category_print(info[tup[0]], tup[1], parent_cat=tup[0])
                print
            except KeyError:
                pass

    if course_categories != None:
        try:
            print
            print "------------------------------------------------"
            print "COURSE INFO".center(45)
            print "------------------------------------------------"
            for course in info['courses']:
                print info['courses'][course]['Title']
                for cat in course_categories:
                    category_print(info['courses'][course], cat)
                print
        except KeyError:
            pass

    print
    return


#============================================================================================
#*****======================================MAIN========================================*****
#============================================================================================

#GLOBAL LISTS
tracking_groups = ['Current Market', 'Potential Market', 'Top Camp', 'Java/.NET', 'Selected Camp']
tracking_groups_files = find_file('*.json','current_data/tracking_groups')
filter_list = ['Tracking Group', 'Location', 'Technology', 'Category', 'Course Attribute', 'Bootcamp']
warning_list = []

#COMMAND LINE OPTION PROCESSING
or_flag = False
summary_flag = False
list_flag = False
sort_flag = False
custom_file = False

for arg in range(len(sys.argv)):
    if sys.argv[arg] == '--or':
        or_flag = True
        sys.argv.remove('--or')
        break

for arg in range(len(sys.argv)):
    if sys.argv[arg] == '--list':
        list_flag = True
        sys.argv.remove('--list')
        break

for arg in range(len(sys.argv)):
    if sys.argv[arg] == '--summary':
        summary_flag = True
        sys.argv.remove('--summary')
        break

for arg in range(len(sys.argv)):
    if sys.argv[arg] == '--sort':
        sort_flag = True
        sys.argv.remove('--sort')
        break

for arg in range(len(sys.argv)):
    if sys.argv[arg] == '--file':
        custom_file = True
        sys.argv.remove('--file')
        datafile = sys.argv[1]
        sys.argv.remove(sys.argv[1])
        if len(datafile) < 12:
            datafile = date_to_file(datafile)
        if os.path.isfile(datafile) == False:
            print 'Could not find the specified file, switching to default data file.'
            print
            datafile = 'current_data/output.json'
        break

#OPEN SEARCH TERM FILE FROM CURRENT DATA AND LOAD CSV DATA INTO SEARCH LIST
#IN THE FORM OF "(term, type)"
search_list = []

search_term_file = 'current_data/search_terms.csv'
with open(search_term_file, 'r') as term_csv:
    search_terms = csv.reader(term_csv)
    for row in search_terms:
        search_list.append((row[0], row[1]))

if len(sys.argv) == 2 and sys.argv[1] == 'terms':
    pprint(search_list)
    sys.exit()

#MATCH ALL OF THE QUERIES WITH SEARCH TERMS TO GET A LIST OF KEYS
key_list = []
for i in range(1, len(sys.argv)):
    key = return_closest(sys.argv[i], search_list, 0.7)
    key_list.append(key)

key_list = [x for x in key_list if x != -1]

#print
#print key_list
#print
if custom_file == False:
    datafile = 'current_data/output.json'

#SORT SEARCH TERMS INTO KEY DICT. IF ONLY ONE TRACKING GROUP AND 'OR' IS ON, USE THAT TRACKING GROUP JSON
tracking_list = []
key_dict = {}

first = True
for key in key_list:
    if key[1] == 'Tracking Group':
        tracking_list.append(key[0])
        if or_flag == False and first == True:
            datafile = str(return_closest(key[0], tracking_groups_files, 0.3))
            first = False
        else:
            continue
    else:
        if key[1] in key_dict.keys():
            key_dict[key[1]].append(key[0])
        else:
            key_dict[key[1]] = [key[0]]
key_dict['Tracking Group'] = tracking_list


#IF NO SEARCH TERMS WENT THROUGH, EXIT THE FUNCITON INSTEAD OF PRINTING ALL
dict_empty = True
for key in key_dict.keys():
    if len(key_dict[key]) > 0:
        dict_empty = False
if dict_empty == True:
    print 'No keys were entered or none of the entered keys were found. Aborting...'
    print
    sys.exit()

print key_dict

#LOAD DATA
with open(datafile) as json_data:
    bootcamps = json.load(json_data)

if 'Meta' in key_dict.keys():
    pprint(bootcamps['meta'])
    sys.exit()

filtered_camps = []

#LOOP THROUGH BOOTCAMPS, FILTER, DISPLAY SELECTED CATEGORIES
for camp in bootcamps:
    try:
        name = bootcamps[camp]['name'].title()
    except KeyError:
        continue

    #*********************FILTERS********************

    if len(key_dict['Tracking Group']) > 0:
        if or_flag == True:
            if any(i in bootcamps[camp]['tracking_groups'] for i in key_dict['Tracking Group']) == False:
                continue
        else:
            if all(i in bootcamps[camp]['tracking_groups'] for i in key_dict['Tracking Group']) == False:
                continue

    #THIS IS WHERE THE 'AND/OR' METHOD CLEARLY NEEDS TO CHANGE, LOCATION ALSO NEEDS TO BE AND/OR (adjusting any/all),
    #SO THERE NEEDS TO BE EITHER A DIFFERENT FLAG SYSTEM OR ANOTHER WAY TO INDICATE WHETHER A FILTER SHOULD BE AND/OR
    #RIGHT NOW, IT'S USING 'ANY', SO IT'S ESSENTIALLY AN 'OR' BY DEFAULT
    try:
        if set(key_dict['Location']).issubset(bootcamps[camp]['locations']) == False:
        #if any(i in bootcamps[camp]['locations'] for i in key_dict['Location']) == False:
            continue
    except KeyError:
        pass
    except TypeError:
        continue

    try:
        #THIS IS 'AND'
        if set(key_dict['Technology']).issubset(bootcamps[camp]['technologies']) == False:
        #THIS WOULD BE 'OR'
        #if any(i in bootcamps[camp]['technologies'] for i in key_dict['Technology']) == False:
            continue
    except KeyError:
        pass
    except TypeError:
        continue

    filtered_camps.append(camp)


    #***************DISPLAY CATEGORIES***************

    categories = []
    course_categories = []
    secondary_categories = []

    try:
        for cat in key_dict['Category']:
            categories.append(cat)
    except KeyError:
        categories = None

    try:
        for cat in key_dict['Course Attribute']:
            course_categories.append(cat)
    except KeyError:
        course_categories = None

    for key in key_dict.keys():
        if key not in filter_list:
            parent_category = key
            for item in key_dict[key]:
                secondary = item
                secondary_categories.append((parent_category, secondary))

    if len(secondary_categories) == 0:
        secondary_categories = None

    try:
        if name in key_dict['Bootcamp']:
            info_print(name, bootcamps[camp], categories, course_categories, secondary_categories)
    except KeyError:
        info_print(name, bootcamps[camp], categories, course_categories, secondary_categories)


if list_flag == True:
    print '==============================================================================================='
    print
    print 'LIST: The following bootcamps fit the inputed tracking group, location, and technology filters:'
    print
    pprint(filtered_camps)
    print

if summary_flag == True:
    try:
        summary_print(bootcamps, categories, filtered_camps)
    except (TypeError, NameError):
        pass
    print

if sort_flag == True:
    try:
        sort_print(bootcamps, categories, filtered_camps)
    except(TypeError, NameError):
        pass

if len(warning_list) > 0:
    print "****************************************************"
    print
    print 'WARNING: The following bootcamps matched the filters'
    print 'but returned no results for the specifed categories:'
    print
    print pprint(warning_list, width=52)
    print
    print "****************************************************"


