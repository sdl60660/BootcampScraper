import tracking
from tracking import tracking_groups

from tracking import tracked_camp_changes
from tracking import tracking_group_stats
from tracking import new_bootcamps

from utilities import return_closest

import numpy as np
import sys
from pprint import pprint

cats = ['locations', 'technologies']
groups = ['Java/.NET', 'Top Camp', 'Selected Camp', 'Potential Markets', 'Current Markets']

def print_stats(print_arrays, max_diff, slack=False):
	for print_array, diff in zip(print_arrays, max_diff):
		if len(print_array[0]) > 0:
			print
			if slack:
				print ('>' + str(print_array[1])).title()
			else:
				print (str(print_array[1])).title()
			print_array = print_array[0]
			for change in print_array:
				pprint(change, indent=4)
			print
			print 'BIGGEST CHANGES: ' + str(diff)
	return

def print_details(detail_tuples):
	tech_array = []
	for x in detail_tuples:
		if x[0] not in tech_array:
			tech_array.append(x[0])
	for tech in tech_array:
		camp_array = []
		for x in detail_tuples:
			if x[0] == tech:
				if x[2] == 'Addition':
					temp_str = str(x[1]) + ' (+)'
				elif x[2] == 'Subtraction':
					temp_str = str(x[1]) + ' (-)'
				camp_array.append(temp_str)
		print str(tech) + ': ' + str(camp_array)

	return

def full_print(days_back, cats, group='ALL'):
	print_arrays, max_diff = tracking_group_stats(days_back, group)
	if any(len(x[0]) > 0 for x in print_arrays):
		print
		print "Changes"
		print "-------"
	print_stats(print_arrays, max_diff)

	detail_array = []
	cat_data_list = []
	for c in cats:
		change_details = tracked_camp_changes(days_back, c, group)
		detail_array.append(change_details)

	if any(len(x) > 0 for x in detail_array):
		print
		print "Details"
		print "-------"
		print
		for x, c in enumerate(cats):
			if len(detail_array[x]) > 0:
				print c.upper()
				print_details(detail_array[x])
				print
	return

def full_slack_print(days_back, cats, group='ALL'):
	print_arrays, max_diff = tracking_group_stats(days_back, group)
	if any(len(x[0]) > 0 for x in print_arrays):
		print
		print "`   Changes   `"
	print_stats(print_arrays, max_diff, slack=True)

	detail_array = []
	cat_data_list = []
	for c in cats:
		change_details = tracked_camp_changes(days_back, c, group)
		detail_array.append(change_details)

	print

	if any(len(x) > 0 for x in detail_array):
		print
		print "`   Details   `"
		print
		for x, c in enumerate(cats):
			if len(detail_array[x]) > 0:
				print ('>' + c).title()
				print_details(detail_array[x])
				print
	return


def main():
	if sys.argv[-1] == 'SLACK':
		slack_command = True
		sys.argv.remove('SLACK')
	else:
		slack_command = False

	if len(sys.argv) < 2:
		print 'USAGE: python tracker_results.py days_back (OPTIONAL:) [tracking_group1] ... [tracking_groupx]'
		sys.exit()

	days_back = int(sys.argv[1])

	#Populate tracking groups with selections from 
	tgroups = []
	for x in range(2, len(sys.argv)):
		tgroups.append(sys.argv[x])

	#Correct any spelling mistakes in command-line input for tracking groups
	for i, item in enumerate(tgroups):
		if item == 'ALL':
			continue
		tgroups[i] = return_closest(item, groups)

	#If input was 'ALL', then print info for all tracking groups
	if len(sys.argv) == 3 and sys.argv[-1].upper() == 'ALL':
		tgroups = groups


	#*******************OVERALL CHANGES********************

	print
	#print '```Overall Changes (Last {} Days)```'.format(days_back)#.center(40, '=')
	print 'Overall Changes (Last {} Days)'.format(days_back).center(40, '=')
	try:
		if slack_command:
			full_slack_print(days_back, cats)
		else:
			full_print(days_back, cats)
	except NameError:
		print
		print 'Could not find file for this date!'
	print

	#****************TRACKING GROUP CHANGES****************

	for group in tgroups:
		print group.center(40, '=')
		try:
			if slack_command:
				full_slack_print(days_back, cats, group)
			else:
				full_print(days_back, cats, group)
		except NameError:
			print
			print 'Could not find file for ' + str(group) + ' tracking group!'
			print
			continue
		print

	#print
	#print ''.center(40,'*')
	#print
	#print 'NEW BOOTCAMPS IN DATASET: ' + str(['{} ({})'.format(str(x[0]), [str('{}').format(y) for y in x[1]] if x[1] else 'No Recorded Locations') for x in new_bootcamps(days_back)])


if __name__ == '__main__':
  main()