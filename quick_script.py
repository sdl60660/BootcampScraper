import sys
import json
import operator
from pprint import pprint

with open('current_data/output.json', 'rb') as current_data:
    data = json.load(current_data)

tech_dict = data['meta']['technologies']

tech_dict = sorted(tech_dict.items(), key=operator.itemgetter(1), reverse=True)

#pprint(tech_dict)
print
for item in tech_dict:
    print str(item[0]) + ": " + str(item[1])
print