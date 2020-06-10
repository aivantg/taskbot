from notion.client import NotionClient
from notion.block import ToggleBlock, BulletedListBlock
from dotenv import load_dotenv
from pprint import pprint
import os

# Setup Environment Variables
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_AUTH_TOKEN")

# Setup Notion Client
client = NotionClient(NOTION_TOKEN)

# Translates Notion Full Names to Users
# Assumes atleast 1 item exists 
def get_users_for_full_names(databaseUrl, full_names):
    names = set(full_names)
    users = {}
    db = client.get_collection_view(databaseUrl)
    for row in db.collection.get_rows():
        assigned = row.assign
        for person in row.assign:
            if person.full_name in names:
                users[person.full_name] = person
                names.remove(person.full_name)
        if len(names) == 0:
            break
    return users

def get_all_items(databaseUrl):
    db = client.get_collection_view(databaseUrl)
    items = []
    for row in db.collection.get_rows():
        items.append({
            "id": row.id,
            "name": row.name,
            "status": row.status,
            "completion_date": row.completion_date and row.completion_date.start,
            "assignees": [person.full_name for person in row.assign]
        })
    return items

def create_notion_row(databaseUrl, properties):
    db = client.get_collection_view(databaseUrl)
    row = db.collection.add_row()
    for key, value in properties.items():
        setattr(row, key, value)
    return row.get_browseable_url()

def delete_notion_row(rowId):
    client.get_block(rowId).remove()

def add_comment_to_notion_row(rowId, discussionId, comment, user):
    row = client.get_block(rowId)
    discussion = [b for b in row.children if b.id == discussionId]
    if len(discussion):
        discussion[0].children.add_new(BulletedListBlock, title=user + ": " + comment)
    else:
        print("Can't find Slack Discussion Toggle")

def update_properties_on_notion_row(databaseUrl, rowId, properties):
    row = client.get_block(rowId)
    for key, value in properties.items():
        setattr(row, key, value)

