import json
import csv
import sys
from pprint import pprint

from difflib import SequenceMatcher

#GLOBAL LISTS
tracking_groups = ['Current Market', 'Potential Market', 'Top Camp', 'Java/.NET']
tracking_groups_files = ['current_markets.json', 'potential_markets.json', 'top_camps.json', 'java_and_NET.json']
filter_list = ['Tracking Group', 'Location', 'Technology', 'Category', 'Course Attribute', 'Bootcamp']
warning_list = []

type1list = ['technologies', 'locations', 'job_guarantee', 'job_assistance','job guarantee', 'job assistance', 'housing', 'visas']


#IF AN INT OR FLOAT, SORT RESULTS BY VALUE; OTHERWISE SORT RESULTS BY BOOTCAMP NAME

#TYPE 1 CATEGORY LOOKUP WILL TAKE A CATEGORY AND OUTPUT A LIST OF "VALUE: # OF BOOTCAMPS THAT FIT VALUE",
#SORTED BY THE # OF BOOTCAMPS THAT FIT
#(technologies, locations, job_guarantee, job_assistance, housing, visas)
def type1_category_lookup(category, data):
    temp_dict = {}
    category = category.lower()

    for bootcamp in data:
        try:
            if type(bootcamps[bootcamp][category]) != list:
                if bootcamps[bootcamp][category]:
                    bootcamps[bootcamp][category] = [bootcamps[bootcamp][category]]
        except KeyError:
            pass

        try:
            for item in bootcamps[bootcamp][category]:
                if item in temp_dict:
                    temp_dict[item] += 1
                else:
                    temp_dict[item] = 1
        except (KeyError, TypeError):
            pass

    val_sort_dict = sorted(temp_dict, key=temp_dict.get, reverse=True)
    key_sort_dict = sorted(temp_dict, reverse=False)

    if category == 'technologies':
        for item in val_sort_dict:
            if len(item) > 1 or item == 'R' or item == 'C':
                try:
                    print str(item) + ": " + str(temp_dict[item])
                except UnicodeEncodeError:
                    pass
        print
        print "-------------------"
        print
        for item in key_sort_dict:
            if len(item) > 1 or item == 'R' or item == 'C':
                print str(item) + ": " + str(temp_dict[item])
    
    else:
        for item in val_sort_dict:
            if len(item) > 1:
                try:
                    print str(item) + ': ' + str(temp_dict[item])
                except UnicodeEncodeError:
                    pass
        print
        print "-------------------"
        print
        for item in key_sort_dict:
            if len(item) > 1:
                try:
                    print str(item) + ": " + str(temp_dict[item])
                except UnicodeEncodeError:
                    pass
    
    return


#=========================================================================================================#
#============================================IN PROGRESS BELOW============================================#
#=========================================================================================================#

#TYPE 2 CATEGORY LOOKUP WILL TAKE A CATEGORY AND OUTPUT A LIST OF "BOOTCAMP NAME: NUMERICAL VALUE"
#SORTED BY VALUE
#(num_courses, num_locations, cr_num_reviews, cr_rating, twitter:followers)
def type2_category_lookup(category, data):
    pass

#VALUE LOOKUP WILL TAKE A VALUE AND CATEGORY AND OUTPUT A LIST OF BOOTCAMPS THAT FIT AND A COUNT
#SORTED BY NUMBER OF COURSE REPORT REVIEWS (NOT PERFECT, BUT OH WELL)
#(specific technology, specific city, tracking group)
def value_lookup(value, category, data):
    pass


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

    if type(info[cat]) is dict:
        print title + ':'
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
                    x = info['courses'][c][cat]
                    empty = False
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

#=========================================================================================================#
#============================================IN PROGRESS ABOVE============================================#
#=========================================================================================================#


#=========================================================================
#*****============================MAIN===============================*****
#=========================================================================

#CHECK FOR 'OR' FLAG AND 'SUMMARY' FLAG
or_flag = False
summary_flag = False

for arg in range(len(sys.argv)):
    if sys.argv[arg] == '--or':
        or_flag = True
        sys.argv.remove('--or')
        break

for arg in range(len(sys.argv)):
    if sys.argv[arg] == '--summary':
        summary_flag = True
        sys.argv.remove('--summary')
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

datafile = 'current_data/output.json'

#CHECK THE KEYS FOR A TRACKING GROUP. IF THERE'S A TRACKING GROUP, USE THAT DATAFILE.
#IF THERE'S MORE THAN ONE TRACKING GROUP AND THE 'OR' FLAG IS TURNED OFF, STILL USE
#THE FIRST ONE'S DATAFILE, AND JUST NARROW FROM WITHIN IT. IF THE 'OR' FLAG IS TURNED
#ON, THEN LOAD FROM MAIN FILE AND JUST FILTER WITH TRACKING GROUP TAGS.
#FOR THE TRACKING GROUP AND THE OTHER KEYS, SORT THEM BY CATEGORY INTO A KEY DICT
tracking_list = []
key_dict = {}

first = True
for key in key_list:
    if key[1] == 'Tracking Group':
        tracking_list.append(key[0])
        if or_flag == False and first == True:
            datafile = 'current_data/tracking_groups/' + str(return_closest(key[0], tracking_groups_files, 0.3))
            first = False
        else:
            continue
    else:
        if key[1] in key_dict.keys():
            key_dict[key[1]].append(key[0])
        else:
            key_dict[key[1]] = [key[0]]

key_dict['Tracking Group'] = tracking_list

print key_dict

#LOAD DATA
with open(datafile) as json_data:
    bootcamps = json.load(json_data)

for camp in bootcamps:
    try:
        name = bootcamps[camp]['name'].title()
    except KeyError:
        continue

    #*********************FILTERS********************

    if len(key_dict['Tracking Group']) > 0:
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

if len(warning_list) > 0:
    print "****************************************************"
    print
    print 'WARNING: The following bootcamps matched the filters'
    print 'but returned no results for the specifed categories:'
    print
    print pprint(warning_list, width=52)
    print
    print "****************************************************"


"""
if key == 'Meta':
    key = key.lower()

"""

#OPTION FOR INPUTING TRACKING GROUPS: this would be a second input and then the output would contain normal results
#but filtered so that they come only from this specific tracking group

#OPTION FOR PARSING THROUGH SECOND LEVEL CATEGORIES: this means that for some categories that are lists, like specific locations,
#or technologies, the output summary should be a list of these objects (i.e. 'Cleveland' or '.NET') followed by the number of bootcamps
#that fit that description.
#Essentially, rather than a summary that looks like 'bootcamp_name: value', it should look like 'value: # of bootcamps'


