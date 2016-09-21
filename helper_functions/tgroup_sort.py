import json
import sys
import os
import datetime

full_output = sys.argv[1]

with open(full_output, 'rb') as full_data:
    data = json.load(full_data)

tracking_groups = ['Java/.NET', 'Potential Markets', 'Current Markets', 'Top Camp', 'Selected Camp']

top_camps = {}
potential_markets = {}
current_markets = {}
java_net = {}
selected_camp = {}

for item in data:
    try:
        if 'Top Camp' in data[item]['tracking_groups']:
            top_camps[item] = data[item]

        if 'Potential Market' in data[item]['tracking_groups']:
            potential_markets[item] = data[item]

        if 'Current Market' in data[item]['tracking_groups']:
            current_markets[item] = data[item]

        if 'Java/.NET' in data[item]['tracking_groups']:
            java_net[item] = data[item]

        if 'Selected Camp' in data[item]['tracking_groups']:
            selected_camp[item] = data[item]
    except KeyError:
        pass

with open('current_data/tracking_groups/top_camps.json', 'w') as tc_data:
    json.dump(top_camps, tc_data, indent=4, sort_keys=True)

with open('current_data/tracking_groups/potential_markets.json', 'w') as pm_data:
    json.dump(potential_markets, pm_data, indent=4, sort_keys=True)

with open('current_data/tracking_groups/current_markets.json', 'w') as cm_data:
    json.dump(current_markets, cm_data, indent=4, sort_keys=True)

with open('current_data/tracking_groups/java_and_NET.json', 'w') as jn_data:
    json.dump(java_net, jn_data, indent=4, sort_keys=True)

with open('current_data/tracking_groups/selected_camps.json', 'w') as sc_data:
    json.dump(selected_camp, sc_data, indent=4, sort_keys=True)
    