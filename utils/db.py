from peewee import *
from datetime import datetime, date
import os
import urllib.parse as urlparse
from utils.slack import get_slack_tag_for_name
from pprint import pprint

if 'DATABASE_URL' in os.environ:
    import psycopg2
    urlparse.uses_netloc.append('postgres')
    url = urlparse.urlparse(os.environ["DATABASE_URL"])
    db = PostgresqlDatabase(database=url.path[1:], user=url.username, password=url.password, host=url.hostname, port=url.port)
else:
    db = SqliteDatabase('bot.db')

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    name = CharField(unique=True)

class Task(BaseModel):
    row_id = CharField(unique=True)
    name = CharField(null=True)
    status = CharField(null=True)
    completion_date = DateField(null=True)
    freshly_created = BooleanField(null=True)
    freshly_completed = BooleanField(null=True)
    new_idea = BooleanField(null=True)

    def to_dict(self):
        return {
            'name': self.name,
            'row_id': self.row_id,
            'status': self.status,
            'completion_date': self.completion_date and self.completion_date.strftime('%a, %m/%d '),
            'days_left': self.completion_date and (self.completion_date - date.today()).days,
            'freshly_created': self.freshly_created,
            'freshly_completed': self.freshly_completed,
            'new_idea': self.new_idea,
            'assignees': [get_slack_tag_for_name(assignee.user.name) for assignee in self.assignees]
        }

class UserTask(BaseModel):
    user = ForeignKeyField(User, backref='tasks')
    task = ForeignKeyField(Task, backref='assignees')

    class Meta:
        indexes = (
            # Specify a unique multi-column index on from/to-user.
            (('user', 'task'), True),
        )


def setup_db():
    db.connect()
    db.create_tables([User, Task, UserTask])

def get_all_tasks_categorized():
    all_task_objects = Task.select()
    all_tasks = [t.to_dict() for t in all_task_objects]
    categories = {}
    categories['freshly_completed'] = [task for task in all_tasks if task['freshly_completed']]
    categories['freshly_created'] = [task for task in all_tasks if task['freshly_created']]
    categories['no_completion_date'] = [task for task in all_tasks if task['status'] != 'Idea' and task['completion_date'] == None]
    categories['new_idea'] = [task for task in all_tasks if task['new_idea']]
    categories['late'] = [task for task in all_tasks if task['days_left'] != None and task['days_left'] < -1 and task['status'] != 'Completed']
    categories['upcoming'] = [task for task in all_tasks if task['days_left'] != None and task['days_left'] >= 0 and task['days_left'] <= 7 and task['status'] != 'Completed']
    categories['horizon'] = [task for task in all_tasks if task['days_left'] != None and task['days_left'] >= 8 and task['days_left'] <=14 and task['status'] != 'Completed']
    return categories

    
def update_db_with_tasks(tasks):
    users = {}
    new_tasks = []


    for task in tasks:
        t, freshly_created = Task.get_or_create(row_id=task["id"])

        freshly_completed = t.status != task['status'] and task['status'] == 'Completed'
        new_idea = t.status != task['status'] and task['status'] == 'Idea'
            
        q = Task.update(name=task['name'], status=task['status'], completion_date=task['completion_date'], freshly_created=freshly_created and not new_idea, freshly_completed=freshly_completed, new_idea=new_idea).where(Task.id == t.id)
        q.execute()

        for assignee in task['assignees']:
            # Create Assignee Record
            if assignee not in users:
                users[assignee], _ = User.get_or_create(name=assignee)
            user = users[assignee]

            # Create UserTask Join Table Record
            try: 
                UserTask.create(user=user, task=t)
            except:
                # If user task already exists, ignore
                pass
        # Return updated tasks   
        if freshly_created or freshly_completed or new_idea:
            new_tasks.append(t)
    return new_tasks


                    
    