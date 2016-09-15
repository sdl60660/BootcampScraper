# -*- coding: utf-8 -*-
import sys
import json
import csv

input_file = 'current_data/output.json'

#LOAD DATA
with open(input_file) as json_data:
    bootcamps = json.load(json_data)

#LIST OF POTENTIAL KEYS TO MATCH THE INPUTS TO
bootcamp_names = []
category_list = []
second_level_list = []
course_attribute_list = []
location_list = []
technology_list = []
search_list = []
tracking_groups = ['Java/.NET', 'Current Market', 'Potential Market', 'Top Camp', 'Selected Camp']

for item in tracking_groups:
    search_list.append((item, 'Tracking Group'))

for item in bootcamps:
    if item == 'meta':
        search_list.append(('meta', 'Meta'))
    else:
        bootcamp_names.append(bootcamps[item]['name'])
        search_list.append((bootcamps[item]['name'], 'Bootcamp'))
        for key in bootcamps[item].keys():
            if key not in category_list:
                category_list.append(key)
                search_list.append((key, 'Category'))
            if type(bootcamps[item][key]) is dict:
                if key == 'courses':
                    for course in bootcamps[item][key]:
                        for ca_key in bootcamps[item][key][course]:
                            if ca_key not in course_attribute_list:
                                course_attribute_list.append(ca_key)
                                search_list.append((ca_key, 'Course Attribute'))
                else:
                    for key2 in bootcamps[item][key].keys():
                        if key2 not in second_level_list:
                            second_level_list.append(key2)
                            search_list.append((key2, key))

        try:
            for loc in bootcamps[item]['locations']:
                if loc not in location_list and item != 'General Assembly':
                    location_list.append(loc)
                    search_list.append((loc, 'Location'))
        except (TypeError, KeyError):
            pass

        try:
            for tech in bootcamps[item]['technologies']:
                if tech not in technology_list and item != 'General Assembly':
                    technology_list.append(tech)
                    search_list.append((tech, 'Technology'))
        except (TypeError, KeyError):
            pass


"""print "BOOTCAMP LIST:", bootcamp_names
print "CATEGORY LIST:", category_list
print "SECOND LEVEL LIST:", second_level_list
print "COURSE ATTRIBUTE LIST:", course_attribute_list
print "TECHNOLOGY LIST:", technology_list
print "LOCATION LIST:", location_list"""

#print "SEARCH LIST:", search_list

if len(sys.argv) == 2:
    output_file = sys.argv[1]
else:
    output_file = 'current_data/search_terms.csv'

with open(output_file, 'w') as out_csv:
    term_csv = csv.writer(out_csv)
    for row in search_list:
        term_csv.writerow(row)
