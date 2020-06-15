import requests as r
from datetime import datetime

day = datetime.today().strftime('%A')
if day == 'Monday' or day == 'Friday':
    r.get('https://bp-eteam-taskbot.herokuapp.com/update_slack')