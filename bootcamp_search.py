import json
import csv
import sys
from pprint import pprint

from difflib import SequenceMatcher

#GLOBAL LISTS
tracking_groups = ['Current Market', 'Potential Market', 'Top Camp', 'Java/.NET']
tracking_groups_files = ['current_markets.json', 'potential_markets.json', 'top_camps.json', 'java_and_NET.json']
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

def info_print(title, info, categories=None):
    string = "INFORMATION FOR BOOTCAMP: " + str(title)
    print
    print "======================================================================"
    print string.center(70)
    print "======================================================================"
    print
    if categories == None:
        pprint(info)
    else:
        if type(categories) == str:
            categories = [categories]
        for cat in categories:
            try:
                if type(info[cat]) is list:
                    print str(cat).title() + ':'
                    pprint(info[cat], indent=4)
                else:
                    print str(cat).title() + ': ' + str(info[cat])
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

    if len(key_dict['Tracking Group']) > 0:
        if all(i in bootcamps[camp]['tracking_groups'] for i in key_dict['Tracking Group']) == False:
            continue

    try:
        categories = []
        for cat in key_dict['Category']:
            categories.append(cat)
    except KeyError:
        categories = None

    try:
        if name in key_dict['Bootcamp']:
            info_print(name, bootcamps[camp], categories)
    except KeyError:
        info_print(name, bootcamps[camp], categories)

"""
if len(sys.argv) == 3:
    file = 'current_data/output.json'
    key = str(sys.argv[1]).title()
    key2 = str(sys.argv[2]).title()
    double_key = True
elif len(sys.argv) == 2:
    file = 'current_data/output.json'
    key = str(sys.argv[1]).title()"""





"""if tracking_group == True:
    if len(sys.argv) == 3:
        
    elif len(sys.argv) == 2:
        key = 'meta'"""

"""
if key == 'Meta':
    key = key.lower()


error_message = True

print
print
print "============================================================"
print "      INFORMATION FOR BOOTCAMP/CATEGORY: " + key
print "============================================================"
print



try:
    pprint(bootcamps[key], width=50)
except KeyError:
    if key.lower() in type1list:
        type1_category_lookup(key, bootcamps)
        error_message = False
    else:
        for camp in bootcamps:
            for category in bootcamps[camp]:
                if str(key) == str(category).title():
                    type2_category_lookup(category, bootcamps)
                    error_message = False
                #else:
                #    match = 
                

                #if double_key == True:

    if error_message == True:
        print 'Sorry! "' + str(key) + '" was not found. Check for spelling or name variations.'

print
print

"""

#OPTION FOR INPUTING TRACKING GROUPS: this would be a second input and then the output would contain normal results
#but filtered so that they come only from this specific tracking group

#OPTION FOR PARSING THROUGH SECOND LEVEL CATEGORIES: this means that for some categories that are lists, like specific locations,
#or technologies, the output summary should be a list of these objects (i.e. 'Cleveland' or '.NET') followed by the number of bootcamps
#that fit that description.
#Essentially, rather than a summary that looks like 'bootcamp_name: value', it should look like 'value: # of bootcamps'


