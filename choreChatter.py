from ssl import CHANNEL_BINDING_TYPES
import string
import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
from datetime import datetime, timedelta

#load environment variable file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

#configure flask; run on default port, automatically update web server
app = Flask(__name__)

#handles slack events
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)

#load token value, pass as token(stores token through environment variable)
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

#gets bot id
BOT_ID = client.api_call("auth.test")['user_id']

#Bot posts message to specified chat
client.chat_postMessage(channel='#tidy-up', text="Hello! I'm your cleaner-upper partner, Chore Chatter! type *start* to begin your walkthrough!")

#counts number of messages
add_chores = {}

#welcome message recieved peeps
welcome_messages = {}

#Trigger words(help, my chores, new chore)
TRIGGER_WORDS = ['help', 'my chores', 'new chore']




#welcome message/ instructions class
class WelcomeMessage:
    START_TEXT = {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': (
                'Welcome to your tidying haven!\n I am ChoreChatter, your personal cleaning helper.'
                '\n*Get started by typing *help* for instructions!*'
            )
        }

    }

    #divider
    DIVIDER = {'type': 'divider'}

    def __init__(self, channel):
        self.channel = channel
        self.icon_emoji = ':soap:'
        self.timestamp =''
        self.completed = False

    #return message to use welcome text
    def get_message(self):
        return {
            'ts': self.timestamp,
            'channel': self.channel,
            'username': 'Welcome!',
            'icon_emoji': self.icon_emoji,
            'blocks': [
                self.START_TEXT,
                self.DIVIDER,
                self._get_reaction_task()
                ]
        }

    #asks for a reaction
    def _get_reaction_task(self):
        checkmark = ':white_check_mark:'
        if not self.completed:
            checkmark = ':white_large_square:'
        
        text = f'{checkmark} *React to this message!*'

        return {'type': 'section', 'text': {'type': 'mrkdwn', 'text': text}}



#bot keeps track of welcome messages for updates
def send_welcome_message(channel, user):
    if channel not in welcome_messages:
        welcome_messages[channel] = {}

    if user in welcome_messages[channel]:
        return

    welcome = WelcomeMessage(channel)
    message = welcome.get_message()
    response = client.chat_postMessage(**message)
    welcome.timestamp = response['ts']

    welcome_messages[channel][user] = welcome





#checks for trigger words
def check_if_trigger_words(message):
    msg = message.lower()
    msg = msg.translate(str.maketrans('', '', string.punctuation))

    return any(word in msg for word in TRIGGER_WORDS)


#bot recieves event, channel, and user info, and responds back
@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

#makes sure bot does not respond to itself
    if user_id != None and BOT_ID != user_id:
        #looks for user id to update counter
        if user_id in add_chores:
             add_chores[user_id] += 1
        else:
            add_chores[user_id] = 1
        
        #starts welcome message
        if text.lower() == 'start':
            send_welcome_message(f'@{user_id}', user_id)
        elif check_if_trigger_words(text):
            ts = event.get('ts')
            client.chat_postMessage(
                channel=channel_id, thread_ts=ts, text="I can help! Please wait...")
            

#looks for reaction to welcome message and keeps track of user id
@ slack_event_adapter.on('reaction_added')
def reaction(payload):
    event = payload.get('event', {})
    channel_id = event.get('item', {}).get('channel')
    user_id = event.get('user')

    if f'@{user_id}' not in welcome_messages:
        return

    welcome = welcome_messages[f'@{user_id}'][user_id]
    welcome.completed = True
    welcome.channel = channel_id
    message = welcome.get_message()
    updated_message = client.chat_update(**message)
    welcome.timestamp = updated_message['ts']
        


#bot command listener
@app.route('/add-chore', methods=['POST'])
def add_chore():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    #makes sure user id is inside add_chore
    message_count = add_chores.get(user_id, 0)

    client.chat_postMessage(channel=channel_id, text="loading...")
    client.chat_postMessage(channel=channel_id, text=f"Message: {message_count}")
    return Response(), 200

#makes sure web server runs if done manually
if __name__ == "__main__":
    app.run(debug=True)
