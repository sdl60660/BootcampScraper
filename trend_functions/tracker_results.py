import sys
sys.path.insert(0,'..')

import tracking
from tracking import tracking_groups

from tracking import tracked_camp_changes
from tracking import tracking_group_stats
from tracking import new_bootcamps

from utilities import return_closest

import numpy as np
from pprint import pprint

cats = ['locations', 'technologies']
groups = ['Java/.NET', 'Top Camp', 'Selected Camp', 'Potential Markets', 'Current Markets']

def intersperse(array, interval):
	temp_array = []
	out_array = []
	count = 2
	for x in array:
		temp_array.append(x)
		if count % interval == 0:
			temp_string = ', '.join(temp_array) + ','
			out_array.append(temp_string)
			out_array.append('\n\t\t\t')
			temp_array = []
		count += 1
	temp_string = ', '.join(temp_array)
	out_array.append(temp_string)
	out_string = ''.join(out_array)
	return out_string

def print_stats(print_arrays, max_diff, slack=False):
	for print_array, diff in zip(print_arrays, max_diff):
		if len(print_array[0]) > 0:
			print
			if slack:
				print ('*' + str(print_array[1]) + '*').title()
			else:
				print (str(print_array[1])).title()
			print_array = print_array[0]
			for change in print_array:
				if slack:
					print '\t\t\t' + change.strip("'")
				else:
					pprint(change, indent=4)
			print
			change_string = ', '.join(['{0} ({1:+d})'.format(str(x[0]), x[1]) for x in diff if x[1] != 0])
			if slack:
				print '\t\t\tBiggest Changes: ' + change_string + '\n\n-----------------------\n'
			else:
				print 'Biggest Changes: ' + change_string + '\n\n-----------------------\n'
	return

def print_details(detail_tuples, slack=False):
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
		tech_list_string = intersperse(camp_array, 3)
		#tech_list_string = ', '.join(camp_array)
		if slack:
			print '\t\t\t*' + str(tech) + '*: ' + str(tech_list_string)
		else:
			print str(tech) + ': ' + str(tech_list_string)

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

def full_slack_print(days_back, cats, details=False, group='ALL'):
	print_arrays, max_diff = tracking_group_stats(days_back, group)
	if any(len(x[0]) > 0 for x in print_arrays):
		print
		print "`-----Changes-----`"
	print_stats(print_arrays, max_diff, slack=True)

	detail_array = []
	cat_data_list = []
	for c in cats:
		change_details = tracked_camp_changes(days_back, c, group)
		detail_array.append(change_details)

	print

	if details:
		if any(len(x) > 0 for x in detail_array):
			print
			print "`-----Details-----`"
			print
			for x, c in enumerate(cats):
				if len(detail_array[x]) > 0:
					print ('*' + c + '*').title()
					print_details(detail_array[x], slack=True)
					print
	return


def main():
	if sys.argv[-1] == 'SLACK':
		slack_command = True
		sys.argv.remove('SLACK')
	else:
		slack_command = False

	details = False
	if 'details' in sys.argv:
		details = True
		sys.argv.remove('details')


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
	if slack_command:
		if days_back == 1:
			day_text = 'Day'
		else:
			day_text = '{} Days'.format(days_back)
		title_text = '`Overall Changes (Last {})`'.format(day_text)
		block_text = '`' + ''.center(len(title_text)-2, '=') + '`'
		print block_text + '\n' + title_text + '\n' + block_text + '\n'
	else:
		print 'Overall Changes (Last {} Days)'.format(days_back).center(40, '=')

	try:
		if slack_command:
			full_slack_print(days_back, cats, details=details)
		else:
			full_print(days_back, cats)
	except NameError:
		print
		print 'Could not find file(s) for some of these dates!'
	print
	print

	#****************TRACKING GROUP CHANGES****************

	for group in tgroups:
		if slack_command:
			if days_back == 1:
				day_text = 'Day'
			else:
				day_text = '{} Days'.format(days_back)
			title_text = '`Tracking Group: {} (Last {})`'.format(group.title(), day_text)
			block_text = '`' + ''.center(len(title_text)-2, '=') + '`'
			print block_text + '\n' + title_text + '\n' + block_text + '\n'
		else:
			print group.center(40, '=')
		try:
			if slack_command:
				full_slack_print(days_back, cats, group)
			else:
				full_print(days_back, cats, group)
		except NameError:
			print
			print 'Could not find file(s) for ' + str(group) + ' tracking group!'
			print
			continue
		print

	if not slack_command:
		print
		print ''.center(40,'*')
		print
		print 'New Bootcamps in Dataset: ' + str(['{} ({})'.format(str(x[0]), [str('{}').format(y) for y in x[1]] if x[1] else 'No Recorded Locations') for x in new_bootcamps(days_back)])

if __name__ == '__main__':
  main()