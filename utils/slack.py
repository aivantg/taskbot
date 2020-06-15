from dotenv import load_dotenv
from datetime import datetime
from pprint import pprint
import requests as r
import os
import slack
import json
from utils.message_templates import get_message_for_category

load_dotenv()

SLACK_TOKEN = os.getenv('SLACK_AUTH_TOKEN')
client = slack.WebClient(token=SLACK_TOKEN)
BOT_ID = client.auth_test()['user_id']

main_channel = 'eteam-tasks'
update_channel = 'eteam-tasks'

data = r.get("https://slack.com/api/conversations.list?types=private_channel&token=" + SLACK_TOKEN).json()
channels = {c['name']: c['id'] for c in data['channels']}

def send_update_message(tasks):
    categories=['late', 'upcoming', 'freshly_completed', 'freshly_created', 'horizon', 'new_idea', 'no_completion_date']
    channel_id = channels[main_channel]

    # Build Message Using Helper Functions
    message = '\n\n-----------------\n'.join([get_message_for_category(category, tasks[category]) for category in categories if tasks[category]])
    message = "Hi, I'm your friendly E-Team Taskbot. Happy " + datetime.today().strftime('%A') + "!\n\nHere's an update for what's been happening in Notion :robot_face:\n\n" + message
    send_message(channel_id, message)

def open_new_task_modal(trigger_id, response_url):
    with open('./utils/new_task_modal.json') as f:
        payload = json.load(f)
    payload['private_metadata'] = response_url
    client.views_open(trigger_id=trigger_id, view=payload)

def open_update_task_modal(trigger_id, response_url):
    with open('./utils/update_task_modal.json') as f:
        payload = json.load(f)
    payload['private_metadata'] = response_url
    client.views_open(trigger_id=trigger_id, view=payload)

def handle_task_create():
    pass

def handle_task_update():
    pass 

def acknowledge_update_modal_submit(task, new_task, response_url, notion_url):
    linked_page = f"<{notion_url}|{task.name}>"
    r.post(response_url, json={'text': f'Your task, "{linked_page}", has been updated', 'response_type': 'ephemeral'})
    channel_id = channels[update_channel]
    nl = "\n"
    message = f"*Update to {'Idea' if task.status == 'Idea' else 'Action Item'}*: {linked_page}"
    message += f"{nl}*New Name*: {new_task['name']}" if new_task['name'] != task.name else ''
    message += f"{nl}*Status*: _{new_task['status']}_"
    message += f"{nl}*Completion Date*: {new_task['completion_date'].strftime('%a, %m/%d ')}"
    message += f"{nl}*Assigned*: {', '.join([get_slack_tag_for_name(p.full_name) for p in new_task['assign']])}"
    send_message(channel_id , message)

def acknowledge_create_modal_submit(task, response_url, notion_url):
    linked_page = f"<{notion_url}|{task['name']}>"
    r.post(response_url, json={'text': f'Your task, "{linked_page}", has been created!', 'response_type': 'ephemeral'})
    channel_id = channels[update_channel]
    nl = "\n"
    send_message(channel_id , f"*New {'Idea' if task['status'] == 'Idea' else 'Action Item'}*: {linked_page}{nl}*Assigned*: {', '.join([get_slack_tag_for_name(p.full_name) for p in task['assign']])}{nl}*Due*: {task['completion_date'].strftime('%a, %m/%d ')}")

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

def get_slack_tag_for_name(full_name):
    slack_id = {
        'Aivant Goyal': '<@U90SE81FY>',
        'Alison Dowski': '<@UCRE9SD62>',
        'Annie Wang': '<@UN6GDUT09>',
        'Micah Yong': '<@UNCUFNMDE>',
        'Karina Nguyen': '<@UCQGDHWHJ>',
        'Myles Domingo': '<@UN05P5HV0>',
        'Ace Chen': '<@UNCUFPQDN>',
    }
    return slack_id[full_name]