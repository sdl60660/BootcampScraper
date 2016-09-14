import json
import sys

input_file = sys.argv[1]
output = sys.argv[2]
datafile = open(input_file, 'rb')
data = json.load(datafile)

new_tech_list = []
new_cr_tech = []
new_su_tech = []

iter_list = [[new_tech_list, 'technologies'],[new_cr_tech, 'cr_technologies'],[new_su_tech, 'su_technologies']]

for camp in data:
    for i, cat in enumerate(iter_list):
        try:
            for tech in data[camp][cat[1]]:
                if not tech in data[camp]['locations']:
                    cat[0].append(tech)
            data[camp][cat[1]] = cat[0]
        except (KeyError, TypeError):
            pass
        cat[0] = []

data['General Assembly']['courses']['Visual Design ']['Location'] = data['General Assembly']['courses']['Visual Design ']['Subjects']
data['General Assembly']['courses']['Visual Design ']['Subjects'] = ['N/A']



output_file = open(output, 'w')
json.dump(data, output_file, indent=4, sort_keys=True)
