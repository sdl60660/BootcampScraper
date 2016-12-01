import json, csv
import os

tracking_groups = ['Java/.NET', 'Selected Camp', 'Top Camp', 'Potential Market', 'Current Market']

def main():
	
	temp_dict = {}
	for group in tracking_groups:
		temp_dict[group] = []

	datafile = open('current_data/output.json', 'r')
	bootcamps = json.load(datafile)
	for camp in bootcamps:
		for key in temp_dict.keys():
			try:
				if key in bootcamps[camp]['tracking_groups']:
					temp_dict[key].append(camp)
			except KeyError:
				pass

	output_file = 'current_data/tracking_groups.json'
	with open(output_file, 'w') as f:
		json.dump(temp_dict, f, indent=4, sort_keys=True)


if __name__ == '__main__':
    main()