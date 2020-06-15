from flask import Flask, request
from utils.notion import *
from utils.slack import *
from utils.db import *
from pprint import pprint
from datetime import datetime
import json
import os

setup_db()
port = os.getenv("PORT") or 3000
main_db_url = "https://www.notion.so/calblueprint/b2b9259d183b40728f0320d1f2650a2f?v=7328da4fadc74800b907b78291f0ddc4"
latest_task_created, latest_task_updated = '', ''

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

@app.route('/update_task', methods = ['POST'])
def update_task():
    open_update_task_modal(request.form['trigger_id'], request.form['response_url'])
    return '' 

@app.route('/new_task', methods = ['POST'])
def new_task():
    open_new_task_modal(request.form['trigger_id'], request.form['response_url'])
    return ''


@app.route('/list_options', methods=['POST'])
def list_options():
    data = json.loads(request.form['payload'])
    action_id = data['action_id']
    query = data['value']
    print(f"Received Query: {query}")
    if action_id == 'task_choose':
        tasks = get_all_tasks()
        options = [{'text': {'type': 'plain_text', 'text': task['name']}, 'value': task['row_id']} for task in tasks if query.lower() in task['name'].lower()]
        return {'options': options}, 200

    return '', 200

@app.route('/modal_submit', methods=['POST'])
def modal_submit():
    global latest_task_created, latest_task_updated
    data = json.loads(request.form['payload'])
    view_name = data['view']['title']['text']
    values = data['view']['state']['values']
    response_url = data['view']['private_metadata']

    if view_name == 'Update Task':
        task_row_id = values['task']['task_choose']['selected_option']['value']
        task = Task.select().where(Task.row_id == task_row_id)[0]

        # Get assignees if value exists
        assignees_val = values['assignees']['action'].get('selected_options')
        print("Assignees Value")
        assign = [all_users[option['value']] for option in assignees_val] if assignees_val else [all_users[assignee.user.name] for assignee in task.assignees]
        print(assignees_val)
        print(assign)

        # Get completion_date if exists
        completion_val = values['completion_date']['action'].get('selected_date')
        completion_date = datetime.strptime(completion_val, '%Y-%m-%d') if completion_val else task.completion_date
        print("Completion Values")
        print(completion_val)
        print(completion_date)

        # Get status if exists
        status_val = values['status']['action'].get('selected_option')
        status = status_val['value'] if status_val else task.status
        print("Status Value")
        print(status_val)
        print(status)
        return '', 200
    elif view_name == 'Create Task':
        # Create new Notion Row
        task = {
            'name': values['name']['title_input']['value'],
            'assign': [all_users[option['value']] for option in values['assignees']['action']['selected_options']],
            'completion_date': datetime.strptime(values['completion_date']['action']['selected_date'], '%Y-%m-%d'),
            'status': 'Idea' if values['is_idea']['action']['selected_option']['value'] == 'yes' else 'Not Started'
            }
        if task['name'] == latest_task_created:
            print("Duplicate Task Found")
            return '', 200
        latest_task_created = task['name']
        notion_url = create_notion_row(main_db_url, task)

        # Respond on Slack
        acknowledge_create_modal_submit(task, response_url, notion_url)
        return '', 200
    
# Start the server by default on port 3000
if __name__ == "__main__":
    app.run(port=port)
