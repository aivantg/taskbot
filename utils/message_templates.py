def get_message_for_category(category, tasks):
    return category_message_templates[category](tasks)


nl = '\n'
basic_task = lambda t: f"{status_emojis[t['status']] or ''}{t['name']}"
basic_task_with_assignees = lambda t: f"{status_emojis[t['status']] or ''}{t['name']}, Assigned: _{', '.join(t['assignees']) if t['assignees'] else 'No One'}_" 
full_task = lambda t: f"{status_emojis[t['status']] or ''}{t['name']}, *Due:* In {t['days_left']} Days, *Assigned:* _{', '.join(t['assignees']) if t['assignees'] else 'No One'}_"
overdue_task = lambda t: f"{status_emojis[t['status']] or ''}{t['name']}, *Due:* {abs(t['days_left'])} Days Ago, *Assigned:* _{', '.join(t['assignees']) if t['assignees'] else 'No One'}_"
create_category_message = lambda header, task_func, tasks: f"*{header}:*{nl*2}- {(nl + '- ').join([task_func(t) for t in tasks])}"

status_emojis = {
    'In Progress': ':construction: ',
    'Not Started': ':no_entry: ',
    'Completed': ':white_check_mark: ',
    'Ideas': ':bulb: '
}
category_message_templates = {
    'freshly_completed': lambda tasks: create_category_message('Completed Tasks', basic_task_with_assignees, tasks),
    'freshly_created': lambda tasks: create_category_message('Newly Created', full_task, tasks),
    'no_completion_date': lambda tasks: create_category_message('Tasks w/o a Completion Date', basic_task_with_assignees, tasks),
    'new_idea': lambda tasks: create_category_message('New Ideas', basic_task_with_assignees, tasks),
    'late': lambda tasks: create_category_message('Overdue Tasks', overdue_task, tasks),
    'upcoming': lambda tasks: create_category_message('Upcoming Tasks (within a week)', full_task, tasks),
    'horizon': lambda tasks: create_category_message('Tasks on the Horizons', full_task, tasks)
}