import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter

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
client.chat_postMessage(channel='#tidy-up', text="Hello! I'm your cleaner-upper partner, Chore Chatter!")



#bot recieves event, channel, and user info, and responds back
@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    #makes sure bot does not respond to itself
    if BOT_ID != user_id:
        #looks for user id to update counter
        if user_id in add_chores:
            add_chores[user_id] += 1
        else:
            add_chores[user_id] = 1
        client.chat_postMessage(channel=channel_id, text=text)

#counts number of messages
add_chores = {}

#bot command listener
@app.route('/add-chore', methods=['POST'])
def add_chore():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    client.chat_postMessage(channel=channel_id, text="loading...")
    return Response(), 200

#makes sure web server runs if done manually
if __name__ == "__main__":
    app.run(debug=True)
