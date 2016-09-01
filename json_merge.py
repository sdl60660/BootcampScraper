import json
from jsonmerge import merge
from jsonmerge import Merger
import sys
from pprint import pprint

#import argparse

#======DICT KEY (for traditional merge)=======
# 1: BOOTCAMPSIN
# 2: SWITCHUP
# 3: COURSEREPORT

#THE ARGPARSE MODULE WOULD BE HELPFUL TO USE IN THE FUTURE, BUT IT'S NOT REALLY NECESSARY FOR THE PURPOSES OF
#THIS ONE OPTIONAL ARGUMENT
"""parser = argparse.ArgumentParser(description='Merge JSON files, with later files taking conflict priority.')
#parser.add_argument('merge files', metavar='files', type=str, nargs='?',
#                    help='a file to be merged')
parser.add_argument('--output', dest='accumulate', action='store_true',
                    help='indicates that last argument is an output file')

args = parser.parse_args()

print args
if --output == True:
    output_file = sys.argv[-1]
    sys.argv = sys.argv[:-1]

"""

#check if the optional output flag was included
#if so, the last filename is the output file
output = False

for arg in range(len(sys.argv)):
    if sys.argv[arg] == '--output':
        output = True
        sys.argv.remove('--output')
        break

if output == True:
    output_file = sys.argv[-1]
    file_array = sys.argv[:-1]
else:
    output_file = 'output.json'
    file_array = sys.argv


#create an array to store json files from spiders
json_files = []

#add json files from scraper directory, specified in command line
for i in range(1, len(file_array)):
    json_files.append(file_array[i])

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

#merge each file included in argument list, with later ones taking conflict priority
for file in bootcamp_data:
    try:
        for x in bootcamp_data[file]:
            name = str(bootcamp_data[file][x]['name']).title()
            if name in output_dict:
                output_dict[name] = merge(output_dict[name], bootcamp_data[file][x])
            else:
                output_dict[name] = bootcamp_data[file][x]
    except TypeError:
        for x in range(len(bootcamp_data[file])):
            name = str(bootcamp_data[file][x]['name']).title()
            if name in output_dict:
                output_dict[name] = merge(output_dict[name], bootcamp_data[file][x])
            else:
                output_dict[name] = bootcamp_data[file][x]

#write merge JSON to output file
with open(output_file, 'w') as f:
    json.dump(output_dict, f, indent=4, sort_keys=True)


print
print "========================================"
print "================SUMMARY================="
print "========================================"
print
print
for file in bootcamp_data:
    print "Total JSON items in file " + str(file) + ": " + str(len(bootcamp_data[file]))
print
print "Total in OUTPUT: " + str(len(output_dict))
print
"""print "Total Similar: " + str(num_similar)
"""