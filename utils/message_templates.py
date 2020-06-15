def get_message_for_category(category, tasks):
    return category_message_templates[category](tasks)




nl = '\n'
basic_task = lambda t: f"{status_emojis.get(t['status']) or ''}*{t['name']}*"
basic_task_with_assignees = lambda t: f"{status_emojis.get(t['status']) or ''}*{t['name']}*, *Assigned*: {', '.join(t['assignees']) if t['assignees'] else 'No One'}" 
full_task = lambda t: f"{status_emojis.get(t['status']) or ''}*{t['name']}*, Due: In {t['days_left']} Days, *Assigned:* {', '.join(t['assignees']) if t['assignees'] else 'No One'}"
overdue_task = lambda t: f"{status_emojis.get(t['status']) or ''}*{t['name']}*, Due: {abs(t['days_left'])} Days Ago, Assigned: {', '.join(t['assignees']) if t['assignees'] else 'No One'}"
create_category_message = lambda header, task_func, tasks: f"*{header}*{nl*2}- {(nl + '- ').join([task_func(t) for t in tasks])}"

slack_id = {
    'Aivant Goyal': '',
    'Alison Dowski': '',
    'Annie Wang': '',
    'Micah Yong': '',
    'Karina Nguyen': '',
    'Myles Domingo': '',
    'Ace Chen': '',
}

status_emojis = {
    'In Progress': ':construction: ',
    'Not Started': ':no_entry: ',
    'Completed': ':white_check_mark: ',
    'Idea': ':bulb: '
}
category_message_templates = {
    'freshly_completed': lambda tasks: create_category_message(':tada: Completed Tasks :tada:', basic_task_with_assignees, tasks),
    'freshly_created': lambda tasks: create_category_message(':new: Newly Created :new: ', full_task, tasks),
    'no_completion_date': lambda tasks: create_category_message(':question: Tasks w/o a Completion Date :question:', basic_task_with_assignees, tasks),
    'new_idea': lambda tasks: create_category_message(':bulb: New Ideas :bulb:', basic_task_with_assignees, tasks),
    'late': lambda tasks: create_category_message(':rotating_light: Overdue Tasks :rotating_light:', overdue_task, tasks),
    'upcoming': lambda tasks: create_category_message(':calendar: Upcoming Tasks :calendar:', full_task, tasks),
    'horizon': lambda tasks: create_category_message(':city_sunrise: Tasks on the Horizons :city_sunrise:', full_task, tasks)
}
