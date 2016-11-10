import testbot
from testbot import handle_command, default_command_data
from testbot import plot_list, tech_list, location_list, bootcamp_list, tracking_groups

import random

stored_command_data = default_command_data
CHANNEL = 'C2GH8CNG4'

command_list = ['plot', 'search']
parameter_list = location_list + tech_list + tracking_groups + ['details', 'list', 'summary', 'sort', 'trend']

for x in range(0,100):
	stored_command_data = default_command_data
	command = random.choice(command_list) + ' '
	if command == 'plot ':
		command += random.choice(['', 'trend']) + ' '
	#if command.startswith('plot'):
	#	command += "'" + random.choice(plot_list) + "' "
	for y in range(0, 5):
		command += "'" + random.choice(parameter_list) + "' "
	try:
		stored_command_data = handle_command(command, CHANNEL, stored_command_data)
	except AttributeError:
		pass