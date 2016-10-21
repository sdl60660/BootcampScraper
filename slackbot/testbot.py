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
from bootcamp_info.utilities import return_closest
from slacker import Slacker
from helpers import input_to_searchkeys, is_number
import datetime

#os.chdir(os.path.dirname(os.path.abspath('bootcamp_info')))
os.chdir('/Users/samlearner/scrapy_projects/bootcamp_info')

# testbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

plot_list = ['locations', 'technologies']
active_start_db = datetime.date.today().toordinal() - datetime.date(2016, 9, 12).toordinal()

default_command_data = {
        'category': [],
        'camps': [],
        'items': {
            'technologies': [],
            'locations': []
        },
        'days': active_start_db,
        'max_items': 10,
        'tracking_group': None,
        'current/trend': True
    }


def handle_command(command, channel, last_search, last_trend, stored_command_data):
    default_emoji = ':key:'
    default_user = 'searchbot'

    emoji = default_emoji
    user = default_user

    plot_search = False
    text_post = False
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."

    if command.lower().startswith('request'):
        slack_client.api_call("chat.postMessage", channel=channel,
            text='Thanks! Your request has been logged.', as_user=False, username=user, icon_emoji=emoji)
        return last_search, last_trend, stored_command_data

    if command.lower().startswith('search'):
        text_post = True
        keys = ['filler'] + input_to_searchkeys(command) + ['Slack']
        if '--plot' in keys:
            keys.remove('--plot')
            plot_search = True
        out_string, result_data = search_wrapper.main(keys)
        last_search = keys
        stored_command_data = default_command_data
        
        for item in plot_list:
            if 'Category' in result_data.key_list.keys() and item in result_data.key_list['Category']:
                stored_command_data['category'].append(item)
        stored_command_data['camps'] = result_data.camps

        print stored_command_data
        print result_data.key_list, result_data.camps

        #response = search_wrapper.main(keys)
        #RUN THROUGH TERMINAL OUTPUT
        command = ''.join(command.split('--plot'))
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
    if plot_search or command.lower().startswith('plot'):
        plot = True
        #GATHER PLOT COMMAND DATA
        pcommands = input_to_searchkeys(command)
        if len(pcommands) < 1:
            plot = False
            text_post = True
            response = "Please enter a category for the plot (i.e. 'technologies', 'locations'). For example: '@testbot plot technologies'\n" \
            "If you'd like to plot the last search, enter '@testbot plot that!' or '@testbot plot search'.\n" \
            "If you'd like to plot the last search as a trend, enter '@testbot plot trend (# of days)'\n"


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

        """commands = command[5:].split('/')
        commands[2] = type_correct(commands[2], False)
        commands[3] = type_correct(commands[3], True)"""
        #print commands[3]


        days_back = stored_command_data['days']
        if pcommands[0].lower() == 'trend':
            c_status = False
            if len(pcommands) > 1 and is_number(pcommands[1]):
                days_back = int(pcommands[1])
        else:
            c_status = stored_command_data['current/trend']

        #This is the right form, but the wrong variable/command positions
        """if pcommands[1].lower() == 'trend' and type(pcommands[2]) is int:
            m_items = int(pcommands[2])
        else:
            m_items = stored_command_data['max_items']"""

        #MAKE PLOT

        if plot_search or return_closest(pcommands[0].lower(), ['that', 'that!'], 0.92):
            plot_file_name, plot_title = tracking.plot_changes(days_back, stored_command_data['category'][0], current_status=c_status,
                max_items=stored_command_data['max_items'], tracking_group=stored_command_data['camps'],
                percentage=True, save_plot=True, slack_post=True, show_plot=False)



        plot_file_name += '.png'
        #input_command = 'python generate_plot.py 10 technologies 12 True True'# + command[7:]
        #response = os.popen(input_command).read()
        emoji = default_emoji
        user = default_user

    if command.lower().startswith('terms'):
        emoji = default_emoji
        user = default_user

    if command.lower().startswith('groups'):
        emoji = default_emoji
        user = default_user






    if text_post:
        #MAKE THE API CALL AS SEARCHBOT
        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=False, username=user, icon_emoji=emoji)
    
    if plot:
        slack = Slacker(os.environ.get('SLACK_BOT_TOKEN'))
        """def upload(self, file_, content=None, filetype=None, filename=None,
               title=None, initial_comment=None, channels=None):"""
        slack.files.upload(plot_file_name, filename=(plot_title + '.png'), title=plot_title, channels=channel)



        """slack_client.api_call("chat.postMessage", channel=channel,
                              text='How many days back would you like to plot for?', as_user=True)"""







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
    stored_command_data = default_command_data
    READ_WEBSOCKET_DELAY = 0.3 # 0.3 second delay between reading from firehose
    search_log = open('logs/slackbot_logs/slackbot_log.txt', 'a')
    request_log = open('logs/slackbot_logs/requests.txt', 'a')
    search_log.write('\n\n\n' + str(datetime.datetime.now())[:-7] + '\n-------------------\n')
    if slack_client.rtm_connect():
        print("TestBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                search_log.write(str(datetime.datetime.now())[11:-7] + ': ' + str(command) + '\n')
                print command.lower()
                if command.lower().startswith('request'):
                    request_log.write(str(datetime.datetime.now())[:-7] + ': ' + str(command)[8:] + '\n\n')
                last_search, last_trend, stored_command_data = handle_command(command, channel, last_search, last_trend, stored_command_data)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
    search_log.close()
    request_log.close()



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
