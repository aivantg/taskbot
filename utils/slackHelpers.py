from dotenv import load_dotenv
from pprint import pprint
import requests as r
from utils.notionUtils import create_notion_row, delete_notion_row, add_comment_to_notion_row, update_properties_on_notion_row
from utils.db import find_tracked_message, track_message, untrack_message
import json
import os
import re
import slack
from bs4 import BeautifulSoup

load_dotenv()

SLACK_TOKEN = os.getenv('SLACK_AUTH_TOKEN')
client = slack.WebClient(token=SLACK_TOKEN)
BOT_ID = client.auth_test()['user_id']

# Translate channels in settings.json from name to ID
with open('utils/settings.json') as f:
  settings = json.load(f)

data = r.get("https://slack.com/api/conversations.list?types=private_channel&token=" + SLACK_TOKEN).json()
watched_channels = {c['id']: c['name'] for c in data['channels'] if settings['channelRules'].get(c['name'])}


# Utility Functions
def send_message(channel, message, thread_ts=None):
    try: 
        return client.chat_postMessage(channel=channel, text=message, thread_ts=thread_ts, unfurl_media="False")['ts']
    except:
        print("Could not send message")

def remove_message(channel, ts):
    try:
        client.chat_delete(channel=channel, ts=ts)
    except:
        print("Could not remove message")

def react_message(channel, ts, reaction):
    try: 
        client.reactions_add(channel=channel, timestamp=ts, name=reaction)
    except:
        print("Could not add Reaction")

def unreact_message(channel, ts, reaction):
    try: 
        client.reactions_remove(channel=channel, timestamp=ts, name=reaction)
    except:
        print("Could not remove Reaction")

def get_username(userId):
    return client.users_info(user=userId)['user']['profile']['real_name']

def get_slack_message(channel, ts):
    return client.conversations_history(latest=ts, channel=channel, limit=1, inclusive="True")['messages'][0]

def receive_message(event):
    if not event.get('text'): # Edge case
        return 
    text, channel, ts, user, thread_ts = event['text'], event['channel'], event['ts'], event['user'], event.get('thread_ts')
    channel_name = watched_channels.get(channel)
    if user and user != BOT_ID and channel_name:
        channel_settings = settings['channelRules'][channel_name]
        process_message(text, channel, ts, user, thread_ts, channel_settings)
        
def receive_reaction(event):
    reaction, channel, user, ts = event['reaction'], event['item']['channel'], event['user'], event['item']['ts']
    channel_name = watched_channels.get(channel)
    if user and user != BOT_ID and channel_name:
        channel_settings = settings['channelRules'][channel_name]
        process_reaction(reaction, channel, ts, user, channel_settings)
        
