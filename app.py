from flask import Flask
from utils.notion import get_all_items
from utils.slack import send_update_message
from pprint import pprint
import os
from utils.db import setup_db, update_db_with_tasks, get_all_tasks_categorized

setup_db()
port = os.getenv("PORT") or 3000

# This `app` represents your existing Flask app
app = Flask(__name__)

@app.route('/update_slack')
def updateSlack():
    # update local task database using latest data from notion
    tasks = get_all_items("https://www.notion.so/calblueprint/b2b9259d183b40728f0320d1f2650a2f?v=7328da4fadc74800b907b78291f0ddc4")
    db_tasks = update_db_with_tasks(tasks)

    # Categorize all tasks and send update message
    task_categories = get_all_tasks_categorized()
    send_update_message('eteam-secret-testing', task_categories)

# Start the server by default on port 3000
if __name__ == "__main__":
    app.run(port=port)
