import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter

#load environment variable file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

#configure flask; run on default port, automatically update web server
app = Flask(__name__)

#load token value, pass as token(stores token through environment variable)
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

#Bot posts message to specified chat
client.chat_postMessage(channel='#tidy-up', text="Hello! I'm your cleaner-upper partner, Chore Chatter!")

#makes sure web server runs if done manually
if __name__ == "__main__":
    app.run(debug=True)
