import os
import time
from slackclient import SlackClient
import sys
sys.path.insert(0,'..')
import search_wrapper
import subprocess
import generate_plot

from search_track_plot_functions import slack_tracker_wrapper

import tracking
from tracking import tracked_camp_changes, tracking_group_stats

MARKETS = ['Cleveland', 'Columbus', 'Pittsburgh', 'Detroit', 'Buffalo', 'Chicago', 'Toronto', 'Cincinnati']

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
SLACK_CHANNEL = '#testbot-test'

#LOCATION MOVES AMONG SELECTED CAMPS OR TO/OUT OF TRACKED MARKETS
#(DO ALL AND THEN NARROW BY CITY BEFORE PASSING TO WRAPPER)

loc_out_string = ''

select_location_changes = tracked_camp_changes(5, 'locations', 'Selected Camp')
full_location_changes = tracked_camp_changes(5, 'locations')

for item in full_location_changes:
	if item[0] in MARKETS and item not in select_location_changes:
		select_location_changes.append(item)

location_changes = slack_tracker_wrapper.location_changes(select_location_changes)
if location_changes != -1:
	for x in location_changes:
		loc_out_string += x +'\n\n'

	slack_client.api_call(
	    "chat.postMessage", channel=SLACK_CHANNEL, text=loc_out_string,
	    username='Competitor Location Moves', icon_emoji=':taxi:'
	)

tech_out_string = ''
tech_changes = slack_tracker_wrapper.technology_changes(tracked_camp_changes(5, 'technologies', 'Selected Camp'))
if tech_changes != -1:
	for x in tech_changes:
		tech_out_string += x +'\n\n'
	slack_client.api_call(
	    "chat.postMessage", channel=SLACK_CHANNEL, text=tech_out_string,
	    username='Competitor Curriculum Updates', icon_emoji=':robot_face:'
	)