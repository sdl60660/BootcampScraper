#CLEANS OUT THE DUPLICATES FROM THE COURSEREPORT JSON (DUE TO FB AND TWITTER FIELDS AND UNKNOWN PROBLEM WITH PIPELINE ON A FEW BOOTCAMPS (i.e. Coding Dojo))

import json
from jsonmerge import merge
from jsonmerge import Merger
import sys
from pprint import pprint

import copy

file = sys.argv[1]
with open(file) as json_data:
    cr_data = json.load(json_data)

output_json = {}

for x, entry in enumerate(cr_data):
    current_name = entry['name']
    if current_name not in output_json.keys():
        output_json[current_name] = entry
    else:
        if len(entry.keys()) > len(output_json[current_name].keys()):
            output_json[current_name] = entry

with open('clean_coursereport_data.json', 'w') as f:
    json.dump(output_json, f, indent=4, sort_keys=True)