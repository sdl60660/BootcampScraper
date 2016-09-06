import json
from jsonmerge import merge
from jsonmerge import Merger
import sys
from pprint import pprint

#GLOBAL LISTS
tracking_groups = ['Current Market', 'Potential Market', 'Top Camp']
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
    temp_dict = {}
    category = category.lower()

    for bootcamp in data:
        try:
            for item in bootcamps[bootcamp][category]:
                if item in temp_dict:
                    temp_dict[item] += 1
                else:
                    temp_dict[item] = 1
        except (KeyError, TypeError):
            pass

    sort_dict = sorted(temp_dict, key=temp_dict.get, reverse=True)

    for item in sort_dict:
        print str(item) + ': ' + str(temp_dict[item])
    
    return

#VALUE LOOKUP WILL TAKE A VALUE AND CATEGORY AND OUTPUT A LIST OF BOOTCAMPS THAT FIT AND A COUNT
#SORTED BY NUMBER OF COURSE REPORT REVIEWS (NOT PERFECT, BUT OH WELL)
#(specific technology, specific city, tracking group)
def value_lookup(value, category, data):
    temp_dict = {}
    category = category.lower()

    for bootcamp in data:
        try:
            for item in bootcamps[bootcamp][category]:
                if item in tech_dict:
                    temp_dict[item] += 1
                else:
                    temp_dict[item] = 1
        except (KeyError, TypeError):
            pass

    sort_dict = sorted(temp_dict, key=temp_dict.get, reverse=True)

    for item in sort_dict:
        print str(item) + ': ' + str(temp_dict[item])
    
    return


#=========================================================================================================#
#============================================IN PROGRESS ABOVE============================================#
#=========================================================================================================#


#=========================================================================
#*****============================MAIN===============================*****
#=========================================================================


if len(sys.argv) == 3:
    file = 'current_data/output.json'
    key = str(sys.argv[1]).title()
    key2 = str(sys.argv[2]).title()
    double_key = True
elif len(sys.argv) == 2:
    file = 'current_data/output.json'
    key = str(sys.argv[1]).title()

if key == 'Meta':
    key = key.lower()

with open(file) as json_data:
    bootcamps = json.load(json_data)


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
                    #if double_key == True:

    if error_message == True:
        print 'Sorry! "' + str(key) + '" was not found. Check for spelling or name variations.'

print
print

#OPTION FOR INPUTING TRACKING GROUPS: this would be a second input and then the output would contain normal results
#but filtered so that they come only from this specific tracking group

#OPTION FOR PARSING THROUGH SECOND LEVEL CATEGORIES: this means that for some categories that are lists, like specific locations,
#or technologies, the output summary should be a list of these objects (i.e. 'Cleveland' or '.NET') followed by the number of bootcamps
#that fit that description.
#Essentially, rather than a summary that looks like 'bootcamp_name: value', it should look like 'value: # of bootcamps'



"""
print "ALSO! (temporarily) Here are some stats on technology usage and bootcamp reviews:"
print"""

"""

tech_dict = {}

for bootcamp in bootcamps:

    try:
        for technology in bootcamps[bootcamp]['technologies']:
            if technology in tech_dict:
                tech_dict[technology] += 1
            else:
                tech_dict[technology] = 1
    except (KeyError, TypeError):
        pass
        #if technology in tech_dict:
         #   tech_dict[technology] += 1
        #else:
        #    tech_dict[technology] = 1

sort_dict = sorted(tech_dict, key=tech_dict.get, reverse=True)

for item in sort_dict:
    if len(item) > 1 or item == 'R' or item == 'C':
        print str(item) + ": " + str(tech_dict[item])

print
print

"""

"""
review_dict = {}

for bootcamp in bootcamps:
    try:
        review_dict[bootcamps[bootcamp]['name']] = bootcamps[bootcamp]['twitter']['followers']
    except (KeyError, TypeError):
        pass

sort_dict = sorted(review_dict, key=review_dict.get, reverse=True)

for item in sort_dict:
    print str(item) + ': ' + str(review_dict[item])

print

"""

#pprint (sorted(tech_dict, key=tech_dict.get, reverse=True), width=50)
