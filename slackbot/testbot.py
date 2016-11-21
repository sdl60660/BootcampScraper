import os, time, sys
sys.path.insert(0,'..')

from slackclient import SlackClient
import search_wrapper
from search_wrapper import main

import subprocess
import tracking
from bootcamp_info.utilities import return_closest
from slacker import Slacker
from helpers import input_to_searchkeys, is_number
import datetime, random, csv

#os.chdir(os.path.dirname(os.path.abspath('bootcamp_info')))
os.chdir('/Users/samlearner/scrapy_projects/bootcamp_info')
from current_data.attribute_dict import Out_Dict, In_Dict

term_list = []
datafile = open('current_data/search_terms.csv', 'r')
search_terms = csv.reader(datafile)
for row in search_terms:
    term_list.append((row[0], row[1]))


# testbot's ID as an environment variable
#BOT_ID = 'U2GEYPJH4'
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

sub_course_cats = ['Cost','Hours/Week', 'Class Size', 'tweets', 'followers']
plot_list = ['technologies'] + [x[0] for x in term_list if x[1] == 'Category' and x[0] != 'technologies'] + sub_course_cats
for cat in ['last_updated', 'twitter', 'accreditation', 'housing', 'cr_technologies', 'visas', 'top_source', 'email', 'website', 'tracking_groups',
'tracks', 'facebook', 'name', 'job_guarantee', 'courses', 'subjects', 'scholarships', 'su_technologies', 'general_cost', 'cost_estimate',
'matriculation_stats']:
    plot_list.remove(cat)
for x in plot_list:
    if x in Out_Dict.keys():
        plot_list.append(Out_Dict[x])

tech_list = [x[0] for x in term_list if x[1] == 'Technology']
location_list = [x[0] for x in term_list if x[1] == 'Location']
bootcamp_list = [x[0] for x in term_list if x[1] == 'Bootcamp']
tracking_groups = ['Java/.NET', 'Selected Camp', 'Top Camp', 'Potential Market', 'Current Market']

active_start_db = datetime.date.today().toordinal() - datetime.date(2016, 9, 12).toordinal()

default_command_data = {
        'category': [],
        'camps': [],
        'technologies': [],
        'locations': [],
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
    while True:
        display_list = [Out_Dict[x] if x in Out_Dict.keys() else x for x in accept_list]
        response = "Please enter {} for the {} (i.e. '{}', '{}')".format(category, action, str(display_list[0]),
            ' '.join(str(display_list[random.randint(1, (len(display_list)-1))]).split('_')))
        slack_client.api_call("chat.postMessage", channel=channel,
                  text=response, as_user=False, icon_emoji=':question:', username='Info Helper Bot')
        reply, channel, user = parse_slack_output(slack_client.rtm_read(), feedback=True)
        if reply:
            if is_number(reply):
                if is_number(reply) in accept_list:
                    return reply
            else:
                x = return_closest(reply.lower(), accept_list, 0.8)
                if x != -1:
                    return x

def populate_category(pcommands, cat_list, stored_command_data, cat):
    if any(return_closest(x, cat_list, 0.8) != -1 for x in pcommands):
        stored_command_data[cat] = []
    for x in pcommands:
        if return_closest(x, cat_list, 0.8) != -1:
            stored_command_data[cat].append(x)
    return stored_command_data

def handle_command(command, channel, stored_command_data):
    default_command_data = {
        'category': [],
        'camps': [],
        'technologies': [],
        'locations': [],
        'days': active_start_db,
        'max_items': 10,
        'tracking_group': None,
        'current/trend': True
    }

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
                stored_command_data['tracking_group'] = [result_data.key_list['Tracking Group'][0]]
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

        input_command = "python trend_functions/tracker_results.py " + command[6:] + " 'Selected Camp' SLACK"
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

        #==============PARSE PLOT COMMAND DATA==============

        #"That" Plot From Search
        if plot_search or return_closest(pcommands[0].lower(), ['that', 'that!'], 0.9) != -1:
            pass
        else:
            stored_command_data = default_command_data

        #Current vs. Trend
        if any(x in pcommands for x in ['trend', 'Trend', 'past', 'Past']):
            c_status = False
            stored_command_data['current/trend'] = False
        else:
            c_status = True
            stored_command_data['current/trend'] = True

        #Days Back
        days_back = stored_command_data['days']

        if 'trend' in pcommands and len(pcommands) > (pcommands.index('trend')+1):
            if is_number(pcommands[pcommands.index('trend')+1]):
                days_back = int(pcommands[pcommands.index('trend')+1])
            elif 'max' in pcommands:
                days_back = active_start_db
        else:
            for x in pcommands:
                if is_number(x):
                    stored_command_data['max_items'] = int(x)
                    break

        #Tracking Groups/Camps
        stored_command_data = populate_category(pcommands, tracking_groups, stored_command_data, 'tracking_group')
        if stored_command_data['tracking_group']:
            stored_command_data['tracking_group'] = stored_command_data['tracking_group'][0]
        stored_command_data = populate_category(pcommands, bootcamp_list, stored_command_data, 'camps')

        #Locations/Technologies
        stored_command_data = populate_category(pcommands, tech_list, stored_command_data, 'technologies')
        stored_command_data = populate_category(pcommands, location_list, stored_command_data, 'locations')
        
        if len(stored_command_data['technologies']) > 0:
            stored_command_data['category'].append('technologies')
        if len(stored_command_data['locations']) > 0:
            stored_command_data['category'].append('locations')
        
        #Categories
        for item in pcommands:
            match = return_closest(item, plot_list, 0.8)
            if match != -1:
                if match in In_Dict.keys():
                    match = In_Dict[match]
                stored_command_data['category'].append(match)
        stored_command_data['category'] = list(set(stored_command_data['category']))

        if len(stored_command_data['category']) == 0:
            stored_command_data['category'] = [request_more_info('category', 'plot', plot_list, channel)]
            if stored_command_data['category'][0] in In_Dict.keys():
                stored_command_data['category'][0] = In_Dict[stored_command_data['category'][0]]
        elif len(stored_command_data['category']) > 1:
            string = "*There were several categories in the last search, some or all of which can be used in a plot. Which would you like to plot?*\n"
            for cat in stored_command_data['category']:
                if cat in Out_Dict.keys():
                    display_cat = Out_Dict[cat]
                else:
                    display_cat = cat.title()
                string += "\t\t\t{}\n".format(display_cat)
            resolved = False
            slack_client.api_call("chat.postMessage", channel=channel,
                  text=string, as_user=False, icon_emoji=':question:', username='Info Helper Bot')
            while resolved == False:
                reply, channel, user = parse_slack_output(slack_client.rtm_read(), feedback=True)
                if reply:
                    if return_closest(reply, In_Dict.keys(), 0.7) != -1:
                        reply = In_Dict[return_closest(reply, In_Dict.keys(), 0.7)]
                    if return_closest(reply, stored_command_data['category'], 0.7) != -1:
                        stored_command_data['category'] = [return_closest(reply, stored_command_data['category'], 0.8)]
                        resolved = True
                    else:
                        text = "Sorry, that doesn't appear to be one of the categories. Check for badly-butchered misspellings or tell Sam that his code is broken."
                        slack_client.api_call("chat.postMessage", channel=channel,
                            text=text, as_user=False, icon_emoji=':question:', username='Info Helper Bot')

        plot_cat = stored_command_data['category'][0]
        if plot_cat in sub_course_cats:
            for x in term_list:
                if x[0] == plot_cat:
                    plot_cat = (x[0], x[1])
                    break
        
        if plot_cat == 'technologies' and len(stored_command_data['technologies']) > 0:
            items = stored_command_data['technologies']
        elif plot_cat == 'locations' and len(stored_command_data['locations']) > 0:  
            items = stored_command_data['locations']
        else:
            items = stored_command_data['max_items']

        if len(stored_command_data['camps']) > 0:
            tgroup_input = stored_command_data['camps']
        else:
            tgroup_input = stored_command_data['tracking_group']

        if 'raw' in pcommands:
            pct = False
        else:
            pct = True
            
        #=====================MAKE PLOT=====================

        print stored_command_data

        plot_file_name, plot_title = tracking.plot_changes(days_back, plot_cat, current_status=c_status,
            max_items=items, tracking_group=tgroup_input,
            percentage=pct, save_plot=True, slack_post=True, show_plot=False)

        if not plot_title:
            plot = False
            text_post = True
            response = plot_file_name
            emoji = ':no_entry_sign:'
            user = 'Error Bot'
        
        plot_file_name += '.png'

    if command.lower().startswith('terms'):
        term_dict = {
            'Bootcamp': [],
            'Tracking Group': [],
            'Category': [],
            'Technology': [],
            'Location': [],
            'Course Attribute': []
        }

        print_lists = []
        command_list = input_to_searchkeys(command)
        print command_list
        if len(command_list) > 0:
            for x in command_list:
                if return_closest(x.title(), term_dict.keys()) != -1:
                    print_lists.append(return_closest(x.title(), term_dict.keys()))
        else:
            print_lists = ['Category', 'Technology', 'Location', 'Course Attribute', 'Tracking Group']

        for term in term_list:
            if term[1].title() in term_dict.keys():
                term_dict[term[1].title()].append(term[0])
            else:
                term_dict['Category'].append(term[0])
        
        response = '\n`------------List Of Search Terms------------`\n\n'

        if len(print_lists) == 0:
            response = 'You either entered an invalid type of search term or something went wrong! Try asking again in the form: "terms [term type 1] [term type 2] etc."'
        else:
            for key in print_lists:
                if key[-1] == 'y':
                    display_key = key[:-1] + 'ies'
                else:
                    display_key = key + 's'
                response += '*' + display_key + '*: '
                for term in term_dict[key]:
                    if term in Out_Dict.keys():
                        response += '`' + str(Out_Dict[term]) + '`, '
                    else:
                        response += '`' + term + '`, '
                response = response[:-2] + '\n\n'

        emoji = ':question:'
        user = 'Info Helper Bot'
        text_post = True

    if command.lower().startswith('groups'):
        emoji = default_emoji
        user = default_user


    #=====================================================================
    #=====================================================================


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

    return stored_command_data

def parse_slack_output(slack_rtm_output, feedback=False):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        #print output_list
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
                command = "'".join(command.split('"'))
                print command.lower()
                if command.lower().startswith('request'):
                    request_log.write(str(datetime.datetime.now())[:-7] + ': ' + str(command)[8:] + ' (' + str(usercode) + ')\n\n')
                #try:
                stored_command_data = handle_command(command, channel, stored_command_data)
                """except TypeError:
                    response = "Sorry, something went wrong with your search. Check your search terms and your quotes or go tell Sam he messed something up."
                    slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=False, username='Error Bot', icon_emoji=':no_entry_sign:')"""
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
