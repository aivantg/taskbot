from dotenv import load_dotenv
from pprint import pprint
import requests as r
import os
import slack
from utils.message_templates import get_message_for_category

load_dotenv()

SLACK_TOKEN = os.getenv('SLACK_AUTH_TOKEN')
client = slack.WebClient(token=SLACK_TOKEN)
BOT_ID = client.auth_test()['user_id']

data = r.get("https://slack.com/api/conversations.list?types=private_channel&token=" + SLACK_TOKEN).json()
channels = {c['name']: c['id'] for c in data['channels']}

def send_update_message(channel_name, tasks):
    categories=['late', 'upcoming', 'freshly_completed', 'freshly_created', 'horizon', 'new_idea', 'no_completion_date']
    try: 
        channel_id = channels[channel_name]
    except:
        raise Exception(f'Invalid Channel Name: {channel_name}')

    # Build Message Using Helper Functions
    message = '\n\n'.join([get_message_for_category(category, tasks[category]) for category in categories if tasks[category]])
    send_message(channel_id, message)

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

