import os
import time
from slackclient import SlackClient
import sys
sys.path.insert(0,'..')
import bootcamp_info.search_wrapper
import subprocess
import bootcamp_info.generate_plot

from bootcamp_info.search_track_plot_functions.slack_tracker_wrapper import location_changes, technology_changes

import bootcamp_info.tracking
from bootcamp_info.tracking import tracked_camp_changes, tracking_group_stats, new_bootcamps

MARKETS = ['Cleveland', 'Columbus', 'Pittsburgh', 'Detroit', 'Buffalo', 'Chicago', 'Toronto', 'Cincinnati']

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
SLACK_CHANNEL = '#testbot-test'

#LOCATION MOVES AMONG SELECTED CAMPS OR TO/OUT OF TRACKED MARKETS
#(DO ALL AND THEN NARROW BY CITY BEFORE PASSING TO WRAPPER)

loc_out_string = ''

select_location_changes = tracked_camp_changes(1, 'locations', 'Selected Camps')
full_location_changes = tracked_camp_changes(1, 'locations')

for item in full_location_changes:
	if item[0] in MARKETS and item not in select_location_changes:
		select_location_changes.append(item)

location_changes = location_changes(select_location_changes)
if location_changes != -1:
	for x in location_changes:
		loc_out_string += x +'\n\n'

	slack_client.api_call(
	    "chat.postMessage", channel=SLACK_CHANNEL, text=loc_out_string,
	    username='Competitor Location Moves', icon_emoji=':taxi:'
	)

tech_out_string = ''
tech_changes = technology_changes(tracked_camp_changes(1, 'technologies', 'Selected Camps'))
if tech_changes != -1:
	for x in tech_changes:
		tech_out_string += x +'\n\n'
	slack_client.api_call(
	    "chat.postMessage", channel=SLACK_CHANNEL, text=tech_out_string,
	    username='Competitor Curriculum Updates', icon_emoji=':robot_face:'
	)

new_camps_string = '\n\n'
camp_changes = new_bootcamps(1)
for camp in camp_changes:
	camp_string = str(camp[0])
	if camp[1]:
		camp_string += ' (Location(s): '
		for loc in camp[1]:
			camp_string += str(loc) + ', '
		camp_string = camp_string[:-2] + ')'
	else:
		camp_string += ' (No Recorded Locations)'
	camp_string += '\n\n'
	new_camps_string += camp_string

if len(camp_changes) > 0:
	slack_client.api_call(
	    "chat.postMessage", channel=SLACK_CHANNEL, text=new_camps_string,
	    username='New Bootcamps in Dataset', icon_emoji=':card_index:'
	)