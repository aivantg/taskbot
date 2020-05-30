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


def save_message_to_notion(ts, channel, text, user, priority, link, channel_settings):
    # Create Row in Notion Database
    names = channel_settings['fieldNames']
    row_data = { names['title']: text, names['user']: user, names['priority']: priority }
    if link:
        row_data[names['link']] = link
    row_id, discussion_id, url = create_notion_row(channel_settings['notionBaseUrl'], row_data)

    # Share info in Slack
    react_message(channel, ts, channel_settings['reactions']['ack'])
    notion_link_ts = send_message(channel, "Notion Link: " + url, ts)
    
    # Save Tracked Message to Database
    track_message(ts, channel, row_id, notion_link_ts, discussion_id)

def remove_message_from_notion(message, channel_settings):
    unreact_message(message.channel, message.ts, channel_settings['reactions']['ack'])
    delete_notion_row(message.notion_row_id)
    remove_message(message.channel, message.notion_link_ts)
    untrack_message(message.ts, message.channel)

def set_priority(message, priority, channel_settings):
    priority_data = {channel_settings['fieldNames']['priority']: priority}
    update_properties_on_notion_row(channel_settings['notionBaseUrl'], message.notion_row_id, priority_data)

# Find Link within Text and Get Page Title
def process_link_message(text):
    text = text.replace('<', '').replace('>', '')
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    if not urls:
        return text, None
    url = str(urls[0])
    title = BeautifulSoup(r.get(url).text, 'lxml').title.string
    if not title: 
        title = url
    return title, url

# Event Handlers

def process_message(text, channel, ts, user, thread_ts, channel_settings):
   print(f"Processing message: '{text}' by {user}") 
   if thread_ts:
        message = find_tracked_message(thread_ts, channel)
        if message:
            add_comment_to_notion_row(message.notion_row_id, message.slack_discussion_node, text, get_username(user))
   else:
        if channel_settings['mode'] == 'manual': # Only process messages from reacts
            return
        trigger = channel_settings['messageTrigger']
        if trigger == 'link':
            text, link = process_link_message(text)
            if not link: # only process messages with links
                return
        else:
            link = None
        save_message_to_notion(ts, channel, text, get_username(user), 'Normal', link, channel_settings)

def process_reaction(reaction, channel, ts, user, channel_settings):
    names, reacts = channel_settings['fieldNames'], channel_settings['reactions']
    message = find_tracked_message(ts, channel)
    if message:
        if reaction == reacts['unsaveMessage']:
            remove_message_from_notion(message, channel_settings)
        if reaction == reacts['normalPriority']:
            set_priority(message, "Normal", channel_settings)
        if reaction == reacts['highPriority']:
            set_priority(message, "High", channel_settings)
        if reaction == reacts['veryHighPriority']:
            set_priority(message, "Very High", channel_settings)
    else:
        if reaction == reacts['saveMessage']:
            slack_message = get_slack_message(channel, ts)
            text, user = slack_message['text'], slack_message['user']
            trigger = channel_settings['messageTrigger']
            if trigger == 'link':
                text, link = process_link_message(text)
                if not link: # only process messages with links
                    return
            else:
                link = None
                save_message_to_notion(ts, channel, text, get_username(user), 'Normal', None, channel_settings)


