from flask import Flask
from utils.slackeventsapi import SlackEventAdapter
from dotenv import load_dotenv
from utils.notionUtils import get_all_items
from pprint import pprint
from playhouse.shortcuts import model_to_dict
import os
# from utils.slackUtils import receive_message, receive_reaction
from utils.db import setup_db, update_db_with_tasks, Task
setup_db()

load_dotenv()
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

# This `app` represents your existing Flask app
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/events", app)

@app.route('/refresh')
def refreshEvents():
    pprint(get_all_items())

tasks = get_all_items("https://www.notion.so/calblueprint/b2b9259d183b40728f0320d1f2650a2f?v=7328da4fadc74800b907b78291f0ddc4")
db_tasks = update_db_with_tasks(tasks)
print(f"Found {len(tasks)} in Notion DB. Created {len(db_tasks)} new tasks in DB")
# pprint([t.to_dict() for t in db_tasks])
pprint([t.to_dict() for t in Task.select()])
    


# Create an event listener for "reaction_added" events and print the emoji name
@slack_events_adapter.on('message')
def message(event, req):
    # ignore retries
    if req.headers.get('X-Slack-Retry-Reason'):
        print("Ignoring Retry")
        return "Status: OK"
    receive_message(event['event'])

@slack_events_adapter.on("reaction_added")
def reaction_added(event, req):
    # ignore retries
    if req.headers.get('X-Slack-Retry-Reason'):
        print("Ignoring Retry")
        return "Status: OK"
    receive_reaction(event['event'])

port = os.getenv("PORT")
if not port:
    port = 3000

# Start the server on port 3000
if __name__ == "__main__":
    app.run(port=port)
