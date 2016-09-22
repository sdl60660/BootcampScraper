import tracking
from tracking import tracking_groups

from tracking import tracked_camp_changes
from tracking import tracking_group_stats

from utilities import return_closest

#import matplotlib.pyplot as plt
import numpy as np

import sys

cats = ['locations', 'technologies']
groups = ['Java/.NET', 'Top Camp', 'Selected Camp', 'Potential Markets', 'Current Markets']

def main():
	if len(sys.argv) < 2:
		print 'USAGE: python tracker_results.py days_back (OPTIONAL:) [tracking_group1] ... [tracking_groupx]'
		sys.exit()

	days_back = int(sys.argv[1])

	tgroups = []
	for x in range(2, len(sys.argv)):
		tgroups.append(sys.argv[x])

	for i, item in enumerate(tgroups):
		if item == 'ALL':
			continue
		tgroups[i] = return_closest(item, groups)

	if sys.argv[2] and sys.argv[2] == 'ALL':
		tgroups = groups


	tracking_group_stats(days_back)

	print

	for c in cats:
		print c.upper()
		print tracked_camp_changes(days_back, c)
		print

	for group in tgroups:
		print group.upper().center(35, '-')
		tracking_group_stats(days_back, group)

		print

		for c in cats:
			print c.upper()
			print tracked_camp_changes(days_back, c, group)
			print

if __name__ == '__main__':
  main()