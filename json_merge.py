import json
from jsonmerge import merge
from jsonmerge import Merger
import sys
from pprint import pprint

import copy

#======DICT KEY=======
# 1: BOOTCAMPSIN
# 2: SWITCHUP
# 3: COURSEREPORT

#create an array to store json files from spiders
json_files = []

#add json files from scraper directory, specified in command line
for i in range(1, len(sys.argv)):
    json_files.append(sys.argv[i])

#create dictionary of numbered keys to bootcamps json files
bootcamp_data = {}
key_num = 0

#load json files
for file in json_files:
    key_num += 1
    with open(file) as json_data:
        bootcamp_data[key_num] = json.load(json_data)

num_similar = 0

output_dict = {}

#THIS COULD BE ADJUSTED SO THAT IT WORKS WITH A VARIABLE NUMBER OF SOURCES
#THAT WAY EVERYTIME I ADD A SPIDER, I DON'T NEED TO COMPLETELY RE-DO THIS
#FUNCTION. ALSO GOING TO NEED TO TAKE INTO ACCOUNT SPIDERS LIKE ALEXA

for x in range(len(bootcamp_data[1])):
    #bootcamp_data[1][x]['sources'] = ['BootcampsIn',]
    name = str(bootcamp_data[1][x]['name']).title()
    output_dict[name] = bootcamp_data[1][x]

for y in range(len(bootcamp_data[2])):
    name = str(bootcamp_data[2][y]['name']).title()
    if name in output_dict:
        #bootcamp_data[2][y]['sources'].append('SwitchUp')
        #source_store = copy.deepcopy(bootcamp_data[2][y]['sources'])
        output_dict[name] = merge(output_dict[name], bootcamp_data[2][y])
        #bootcamp_data[2][y]['sources'] = source_store
    else:
        #bootcamp_data[2][y]['sources'] = ['SwitchUp',]
        output_dict[name] = bootcamp_data[2][y]

for z in bootcamp_data[3]:
    name = str(bootcamp_data[3][z]['name']).title()
    if name in output_dict:
        #bootcamp_data[3][z]['sources'].append('CourseReport')
        #source_store = copy.deepcopy(bootcamp_data[3][z]['sources'])
        output_dict[name] = merge(output_dict[name], bootcamp_data[3][z])
        #bootcamp_data[3][z]['sources'] = source_store
    else:
        #bootcamp_data[3][z]['sources'] = ['CourseReport',]
        output_dict[name] = bootcamp_data[3][z]

with open('output.json', 'w') as f:
    json.dump(output_dict, f, indent=4, sort_keys=True)


"""
print
print "========================================"
print "================SUMMARY================="
print "========================================"
print"""
print
print "Total in BootcampsIn JSON: " + str(len(bootcamp_data[1]))
print "Total in SwitchUp JSON: " + str(len(bootcamp_data[2]))
print "Total in CourseReport JSON: " + str(len(bootcamp_data[3]))
print
"""print "Total Similar: " + str(num_similar)
print
#pprint(bootcamp_data[1][1]['name'], width=100)
#print
#print len(bootcamp_data[1])
"""



"""
result = merge(bootcamp_data[1], bootcamp_data[2])

print
print
print "ORIGNAL 1"
print "---------"
print
pprint(bootcamp_data[1])
print
print
print "ORIGNAL 2"
print "---------"
print
pprint(bootcamp_data[2])
print
print
print "  MERGED  "
print "----------"
print
pprint(result, width= 100)

#print bootcamp_data['file1']
"""