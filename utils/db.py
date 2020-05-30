from peewee import *
import datetime
import os
import urllib.parse as urlparse
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

    def to_dict(self):
        return {
            'name': self.name,
            'row_id': self.row_id,
            'status': self.status,
            'completion_date': self.completion_date,
            'assignees': [assignee.user.name for assignee in self.assignees]
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

    
def update_db_with_tasks(tasks):
    users = {}
    new_tasks = []


    # TODO: categorize each task into "newly completed" "new idea", etc
    for task in tasks:
        t, created = Task.get_or_create(row_id=task["id"])
        print(t.id)
        q = Task.update(name=task['name'], status=task['status'], completion_date=task['completion_date']).where(Task.id == t.id)
        q.execute()
        for assignee in task['assignees']:
            if assignee not in users:
                users[assignee], _ = User.get_or_create(name=assignee)
            user = users[assignee]
            try: 
                UserTask.create(user=user, task=t)
            except:
                # If user task already exists, ignore
                pass
        if created:
            new_tasks.append(t)
    return new_tasks


                    
    