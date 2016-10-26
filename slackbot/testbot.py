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
import random

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
tracking_groups = ['Java/.NET', 'Selected Camp', 'Top Camp', 'Potential Market', 'Current Market']
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

def insert_option_tags(command_string):
    options = ['list', 'sort', 'summary', 'details', 'warnings', 'file', 'all', 'plot']
    new_command_string = command_string
    for x in options:
        if x in new_command_string.lower() and new_command_string[new_command_string.find(x)-1] == ' ':
            new_command_string = new_command_string[:new_command_string.find(x)] + \
            '--' + new_command_string[new_command_string.find(x):]
            new_command_string.replace(x[new_command_string.find(x):new_command_string.find(x)+len(x)], x)
    return new_command_string

def request_more_info(category, action, accept_list, channel):
    loop = True
    while loop:
        response = "Please enter {} for the {} (i.e. {}, {})".format(category, action, accept_list[0],
            accept_list[random.randint(1, (len(accept_list)-1))])
        slack_client.api_call("chat.postMessage", channel=channel,
                  text=response, as_user=False, icon_emoji=':question:', username='Info Helper Bot')
        reply, channel, user = parse_slack_output(slack_client.rtm_read(), feedback=True)
        if reply:
            x = return_closest(reply.lower(),accept_list, 0.8)
            if x != -1:
                loop = False
                return x

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

    if command.lower().startswith('upload data'):
        slack = Slacker(os.environ.get('SLACK_BOT_TOKEN'))
        slack.files.upload('current_data/output.json', filename='{}_bc_data.json'.format(str(datetime.date.today())), title=('Current BC Data JSON ({})'.format(str(datetime.date.today()))), channels=channel)

    if command.lower().startswith('search'):
        command = insert_option_tags(command)
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

        if 'Technology' in result_data.key_list.keys() or 'Location' in result_data.key_list.keys():
            stored_command_data['camps'] = result_data.camps
            stored_command_data['tracking_group'] = None
        elif 'Tracking Group' in result_data.key_list.keys():
            if len(result_data.key_list['Tracking Group']) == 1:
                stored_command_data['tracking_group'] = result_data.key_list['Tracking Group'][0]
                stored_command_data['camps'] = []
            else:
                stored_command_data['camps'] = result_data.camps
                stored_command_data['tracking_group'] = None
        else:
            stored_command_data['tracking_group'] = None

        print stored_command_data
        print result_data.key_list, result_data.camps

        #response = search_wrapper.main(keys)
        #RUN THROUGH TERMINAL OUTPUT
        command = ''.join(command.split('--plot'))

        input_command = 'python search_wrapper.py ' + command[7:] + ' Slack'
        response = os.popen(input_command).read()
        emoji = default_emoji
        user = default_user

    if command.lower().startswith('trend'):
        stored_command_data = default_command_data
        text_post = True
        os.chdir('/Users/samlearner/scrapy_projects/bootcamp_info')
        stored_command_data['current/trend'] = False

        for x in input_to_searchkeys(command):
            if x.title() in tracking_groups:
                stored_command_data['tracking_group'] = x.title()
            elif is_number(x):
                stored_command_data['days'] = int(x)
            elif x.lower() == 'max':
                stored_command_data['days'] = active_start_db

        if 'max' in command.lower():
            command = command.replace('max', str(active_start_db))

        input_command = 'python search_track_plot_functions/tracker_results.py ' + command[6:] + ' SLACK'
        print input_command
        response = os.popen(input_command).read()
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
            response = "Please enter a category for the plot (i.e. 'technologies', 'locations'). For example: `@testbot plot technologies`\n" \
            "If you'd like to plot the last search, enter `@testbot plot that!` or `@testbot plot search`.\n" \
            "If you'd like to plot the last search as a trend, enter `@testbot plot trend [# of days]`\n"
            slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=False, username=user, icon_emoji=emoji)
            return last_search, last_trend, stored_command_data

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

        days_back = stored_command_data['days']
        if pcommands[0].lower() == 'trend':
            c_status = False
            if len(pcommands) > 1:
                if is_number(pcommands[1]):
                    days_back = int(pcommands[1])
                elif pcommands[1].lower() == 'max':
                    days_back = active_start_db
        else:
            c_status = stored_command_data['current/trend']

        #MAKE PLOT
        if len(stored_command_data['camps']) > 0:
            tgroup_input = stored_command_data['camps']
        else:
            tgroup_input = stored_command_data['tracking_group']

        if plot_search or return_closest(pcommands[0].lower(), ['that', 'that!'], 0.92):
            if len(stored_command_data['category']) == 0:
                stored_command_data['category'].append(request_more_info('category', 'plot', plot_list, channel))

            plot_file_name, plot_title = tracking.plot_changes(days_back, stored_command_data['category'][0], current_status=c_status,
                max_items=stored_command_data['max_items'], tracking_group=tgroup_input,
                percentage=True, save_plot=True, slack_post=True, show_plot=False)

        plot_file_name += '.png'
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
        slack.files.upload(plot_file_name, filename=(plot_title + '.png'), title=plot_title, channels=channel)



        """slack_client.api_call("chat.postMessage", channel=channel,
                              text='How many days back would you like to plot for?', as_user=True)"""



    """slack_client.api_call("chat.postMessage", channel=channel,
                              text=last_command, as_user=False, username=user, icon_emoji=emoji)"""

    return last_search, last_trend, stored_command_data

def parse_slack_output(slack_rtm_output, feedback=False):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        print output_list
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel'], output['user']
            if feedback:
                if output and 'text' in output and 'bot_id' not in output:
                    return output['text'].strip().lower(), output['channel'], output['user']
    return None, None, None


if __name__ == "__main__":
    last_search = None
    last_trend = None
    stored_command_data = default_command_data
    READ_WEBSOCKET_DELAY = 0.3 # 0.3 second delay between reading from firehose
    search_log = open('logs/slackbot_logs/slackbot_log.txt', 'a')
    request_log = open('logs/slackbot_logs/requests.txt', 'a')
    search_log.write('\n\n\n' + str(datetime.datetime.now())[:-7] + '\n-------------------\n')
    if slack_client.rtm_connect():
        print 'TestBot connected and running!'
        while True:
            command, channel, usercode = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                search_log.write(str(datetime.datetime.now())[11:-7] + ': ' + str(command) + ' (' + str(usercode) + ')\n')
                print command.lower()
                if command.lower().startswith('request'):
                    request_log.write(str(datetime.datetime.now())[:-7] + ': ' + str(command)[8:] + ' (' + str(usercode) + ')\n\n')
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
