from flask import Flask, request
from utils.notion import get_all_items, get_users_for_full_names, create_notion_row
from utils.slack import send_update_message, open_new_task_modal, acknowledge_modal_submit
from pprint import pprint
from datetime import datetime
import json
import os
from utils.db import setup_db, update_db_with_tasks, get_all_tasks_categorized

setup_db()
port = os.getenv("PORT") or 3000
main_db_url = "https://www.notion.so/calblueprint/b2b9259d183b40728f0320d1f2650a2f?v=7328da4fadc74800b907b78291f0ddc4"
latest_task = ''

# cache db of all users so that we don't have to re-fetch each time
all_users = get_users_for_full_names(main_db_url, ['Aivant Goyal', 'Alison Dowski', 'Annie Wang', 'Ace Chen', 'Myles Domingo', 'Micah Yong', 'Karina Nguyen'])

# This `app` represents your existing Flask app
app = Flask(__name__)

@app.route('/update_slack', methods = ['GET', 'POST'])
def updateSlack():
    # update local task database using latest data from notion
    tasks = get_all_items(main_db_url)
    db_tasks = update_db_with_tasks(tasks)

    # Categorize all tasks and send update message
    task_categories = get_all_tasks_categorized()
    send_update_message(task_categories)
    return ''


@app.route('/new_task', methods = ['POST'])
def new_task():
    open_new_task_modal(request.form['trigger_id'], request.form['response_url'])
    return ''

@app.route('/create_task', methods=['POST'])
def create_task():
    global latest_task
    data = json.loads(request.form['payload'])
    values = data['view']['state']['values']

    # Create new Notion Row
    task = {
        'name': values['name']['title_input']['value'],
        'assign': [all_users[option['value']] for option in values['assignees']['action']['selected_options']],
        'completion_date': datetime.strptime(values['completion_date']['action']['selected_date'], '%Y-%m-%d'),
        'status': 'Idea' if values['is_idea']['action']['selected_option']['value'] == 'yes' else 'Not Started'
        }
    if task['name'] == latest_task:
        print("Duplicate Task Found")
        return '', 200
    latest_task = task['name']

    notion_url = create_notion_row(main_db_url, task)

    # Respond on Slack
    response_url = data['view']['private_metadata']
    acknowledge_modal_submit(task, response_url, notion_url)
    return '', 200
    
# Start the server by default on port 3000
if __name__ == "__main__":
    app.run(port=port)
