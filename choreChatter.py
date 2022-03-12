import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
import time

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

#counts number of messages
add_chores = {}

#bot recieves event, channel, and user info, and responds back
@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    #makes sure bot does not respond to itself
    if BOT_ID != user_id:
        if user_id in add_chores:
            add_chores[user_id] += 1
        else:
            add_chores[user_id] = 1
        client.chat_postMessage(channel=channel_id, text=text)

#schedules message
def scheduleMessage(channel_id):
    result = client.conversations_history(
        channel=channel_id
    )
    message = result["messages"][-1]
    timestamp = message["text"]
    timestamp = timestamp * 60
    time.sleep(timestamp)
    client.chat_postMessage(channel=channel_id, text="This is your reminder for the next chore")

#bot command listener
@app.route('/add-chore', methods=['POST'])
def add_chore():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    #makes sure user_id is inside add_chores
    add_chore = add_chores.get(user_id, 0)
    client.chat_postMessage(channel=channel_id, text=f"ChoreCount: {add_chores}")
    scheduleMessage()
    return Response(channel_id), 200

