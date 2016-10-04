import os
import time
from slackclient import SlackClient
import sys
sys.path.insert(0,'..')
import search_wrapper #tracking, tracker_results, generate_plot, utilities
import subprocess
import generate_plot

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

#2. ADD FUNCTIONALITY FOR RETURNING A PLOT (DON'T KNOW IF ANYTHING NEEDS TO BE DONE ON THIS END)
#3. HANDLE NON-SEARCH REQUESTS (I.E. JUST 'PLOT')
#4. PUSH TRACKING/UPDATES THROUGH ON A SCHEDULE (NOT JUST WHEN PROMPTED)

def handle_command(command, channel, prompted):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."

    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"
    

    if command.startswith('search'):
        #keys = input_to_searchkeys(command)[1:]
        #keys.append('Slack')
        #response = search_wrapper.main(keys)

        #RUN THROUGH TERMINAL OUTPUT
        input_command = 'python search_wrapper.py ' + command[7:] + ' Slack'
        print input_command
        response = os.popen(input_command).read()

    if prompted == True:
        command_text = command.lower()
        if command_text.startswith('stop'):
            prompted = False
            response = "Got it! I won't do that anymore..."

        try:
            days_back = int(str(command))
            response = str(days_back) + ' days back'
            prompted = False
        except ValueError:
            response = "Sorry, that is not a valid number of days.\n" \
            "Please enter another number or enter 'stop' to abort..."
    
    if any(command.startswith(x) for x in test_list):
        response = "How many days back would you like to see changes for?"
        prompted = True

    #DOESN'T WORK YET, BUT SHOULD PROMPT A PLOT TO BE SENT THROUGH
    if command.startswith('plot'):
        input_command = 'python generate_plot.py 10 technologies 12 True True'# + command[7:]
        response = os.popen(input_command).read()

    #DOESN'T WORK YET, BUT SHOULD PROMPT A HELP TEXT TO BE SENT
    if command.startswith('help'):
        if len(command) < 6:
            response = full_help_text
        else:
            help_key = command[5:]

            response = 'SPECIFIC COMMAND HELP GOES HERE'
    
    #MAKE THE API CALL AS SEARCHBOT
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=False, username='searchbot', icon_emoji=':key:')

    return prompted

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
    prompted = False
    READ_WEBSOCKET_DELAY = 0.3 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("TestBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                prompted = handle_command(command, channel, prompted)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")




"""def input_to_searchkeys(command):
    command = command.split(' ')
    searchkeys = []
    x = 0
    while x < len(command):
        if command[x][0:2] == '--':
            searchkeys.append(str(command[x]))
            x += 1
        elif x == len(command)-1:
            searchkeys.append(str(command[x][1:-1]))
            x += 1
        elif command[x][0] == "'" and command[x][-1] != "'":
            found = False
            y = x
            full = command[x]
            while found == False:
                full = ' '.join([full, command[y+1]])
                y += 1
                if command[y][-1] == "'":
                    found = True
            searchkeys.append(str(full[1:-1]))
            x += 1 + (y-x)
        else:
            searchkeys.append(str(command[x][1:-1]))
            x += 1
    return searchkeys"""
