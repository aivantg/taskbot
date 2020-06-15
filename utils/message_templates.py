def get_message_for_category(category, tasks):
    return category_message_templates[category](tasks)




nl = '\n'
basic_task = lambda t: f"{status_emojis.get(t['status']) or ''}*{t['name']}*"
basic_task_with_assignees = lambda t: f"{status_emojis.get(t['status']) or ''}*{t['name']}*, Assigned: {', '.join(t['assignees']) if t['assignees'] else '_No One_'}" 
full_task = lambda t: f"{status_emojis.get(t['status']) or ''}*{t['name']}*, Due: _In {t['days_left']} Days_, Assigned: {', '.join(t['assignees']) if t['assignees'] else '_No One_'}"
overdue_task = lambda t: f"{status_emojis.get(t['status']) or ''}*{t['name']}*, Due: _{abs(t['days_left'])} Days Ago_, Assigned: {', '.join(t['assignees']) if t['assignees'] else '_No One_'}"
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
    'freshly_completed': lambda tasks: create_category_message(':tada: COMPLETED TASKS :tada:', basic_task_with_assignees, tasks),
    'freshly_created': lambda tasks: create_category_message(':new: NEWLY CREATED :new: ', full_task, tasks),
    'no_completion_date': lambda tasks: create_category_message(':question: TASKS W/O A COMPLETION DATE :question:', basic_task_with_assignees, tasks),
    'new_idea': lambda tasks: create_category_message(':bulb: NEW IDEAS :bulb:', basic_task_with_assignees, tasks),
    'late': lambda tasks: create_category_message(':rotating_light: OVERDUE TASKS :rotating_light:', overdue_task, tasks),
    'upcoming': lambda tasks: create_category_message(':calendar: UPCOMING TASKS :calendar:', full_task, tasks),
    'horizon': lambda tasks: create_category_message(':city_sunrise: TASKS ON THE HORIZON :city_sunrise:', full_task, tasks)
}
