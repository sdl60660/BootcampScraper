import os
import time
from slackclient import SlackClient
import sys
sys.path.insert(0,'..')
import search_wrapper #tracking, tracker_results, generate_plot, utilities
from search_wrapper import main
import subprocess
import generate_plot
import tracking
from slacker import Slacker
from helpers import input_to_searchkeys

#os.chdir(os.path.dirname(os.path.abspath('bootcamp_info')))
os.chdir('/Users/samlearner/scrapy_projects/bootcamp_info')

# testbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

test_list = ['testing', 'technologies']


def handle_command(command, channel, last_search, last_trend, stored_command_data):
    default_emoji = ':key:'
    default_user = 'searchbot'

    emoji = default_emoji
    user = default_user
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."


    if command.lower().startswith('search'):
        keys = ['filler'] + input_to_searchkeys(command) + ['Slack']
        out_string, result_data = search_wrapper.main(keys)
        print result_data.key_list, result_data.camps
        #response = search_wrapper.main(keys)
        #RUN THROUGH TERMINAL OUTPUT
        input_command = 'python search_wrapper.py ' + command[7:] + ' Slack'
        response = os.popen(input_command).read()
        emoji = default_emoji
        user = default_user






    if command.lower().startswith('trends'):
        os.chdir('/Users/samlearner/scrapy_projects/bootcamp_info')
        input_command = 'python search_track_plot_functions/tracker_results.py ' + command[7:] + ' SLACK'
        #print input_command
        response = os.popen(input_command).read()
        #response = "How many days back would you like to see changes for?"
        #prompted = True
        emoji = ':chart_with_upwards_trend:'
        user = 'trendbot'







    plot = False
    if command.lower().startswith('plot'):

        #GATHER PLOT COMMAND DATA



        #PARSE PLOT COMMAND DATA
        def type_correct(command, string):
            try:
                command = int(command)
            except ValueError:
                command = command.split(',')
                for i, x in enumerate(command):
                    command[i] = x.strip().strip("'").strip('"')
                if len(command) == 1:
                    if string:
                        command = str(command[0])
            return command

        commands = command[5:].split('/')
        commands[2] = type_correct(commands[2], False)
        commands[3] = type_correct(commands[3], True)
        #print commands[3]

        #MAKE PLOT
        plot_file_name, plot_title = tracking.plot_changes(int(commands[0]), str(commands[1]), current_status=True, max_items=commands[2],
            tracking_group=commands[3], percentage=True, save_plot=True, slack_post=True, show_plot=False)
        plot_file_name += '.png'
        #input_command = 'python generate_plot.py 10 technologies 12 True True'# + command[7:]
        #response = os.popen(input_command).read()
        emoji = default_emoji
        user = default_user
        plot = True

    if command.lower().startswith('terms'):
        emoji = default_emoji
        user = default_user

    if command.lower().startswith('groups'):
        emoji = default_emoji
        user = default_user
    
    if plot:
        slack = Slacker(os.environ.get('SLACK_BOT_TOKEN'))
        """def upload(self, file_, content=None, filetype=None, filename=None,
               title=None, initial_comment=None, channels=None):"""
        slack.files.upload(plot_file_name, filename=(plot_title + '.png'), title=plot_title, channels=channel)
        slack_client.api_call("chat.postMessage", channel=channel,
                              text='How many days back would you like to plot for?', as_user=True)
        #slack_client.api_call('files.upload', file=plot_file_name, channel=channel, filename=(plot_title + '.png'), title=plot_title)
    else:
        #MAKE THE API CALL AS SEARCHBOT
        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=False, username=user, icon_emoji=emoji)







    """slack_client.api_call("chat.postMessage", channel=channel,
                              text=last_command, as_user=False, username=user, icon_emoji=emoji)"""

    return last_search, last_trend, stored_command_data

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    last_search = None
    last_trend = None
    stored_command_data = {}
    READ_WEBSOCKET_DELAY = 0.3 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("TestBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                last_search, last_trend, stored_command_data = handle_command(command, channel, last_search, last_trend, stored_command_data)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")



    #DOESN'T WORK YET, BUT SHOULD PROMPT A HELP TEXT TO BE SENT
    """if command.startswith('help'):
        full_help_text = 'Bootcamp Slackbot Help\n'
        full_help_text += '===================\n\n'
        full_help_text += '-Begin all commands with @bootcampbot\n'
        full_help_text += '-Can be used to search camps and features of camps, plot data or look at trends\n\n\n'
        full_help_text += 'Commands\n'
        full_help_text += '---------------\n'
        full_help_text += 'search: gives a list of camps that fit given location, technology or tracking group filters\n'
        full_help_text += 'plot:\n'
        full_help_text += 'trend:\n'

        if len(command) < 6:
            response = full_help_text
        else:
            help_key = command[5:]

            response = 'SPECIFIC COMMAND HELP GOES HERE'"""
