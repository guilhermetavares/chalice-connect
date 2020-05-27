import os
import re
import random

from chalice import Chalice, Cron

from chalicelib.gitlab import GitlabClient
from chalicelib.slack import SlackClient


AUTHOS_LIST_IDS = os.environ.get('AUTHOS_LIST_IDS', '')
AUTHOS_LIST_IDS = re.findall(r'\d+', AUTHOS_LIST_IDS)

GITLAB_REPO_LIST_IDS = os.environ.get('GITLAB_REPO_LIST_IDS', '')
GITLAB_REPO_LIST_IDS = re.findall(r'\d+', GITLAB_REPO_LIST_IDS)


class Notification(object):
    AUTHORS = AUTHOS_LIST_IDS

    def send_to_slack(self):
        data = self._format_data()
        SlackClient().message(data)
    
    def _message(self):
        MESSAGES = [
            "Fala meus consagrados, temos vários MR pendentes vamos ajudar!",
            "E aí meus cumpadis, vamos olhar um MR hoje?",
            "Estamos comemorando bar-mitza desses MR, vamos ajudar?",
            "Jovens e jovas, seguem os MR em aberto de hoje",
            "O povo bunito! Vamos ver um MR pra liberar os amiguinhos!",
            "A cada 15 minutos, um MR é esquecido no Brasil! Vamos contribuir!",
            "Faça como eu, revise os MR dos seus amigos!",
            "Olha o ronaldinho!",
            "Olhas os MRs aí gente!",
        ]
        return random.choice(MESSAGES)


    def _format_data(self):
        data = {
           	"text": self._message(),
        	"username": "Fabiao",
        	"mrkdwn": True,
            "attachments": []
        }

        for project_id in GITLAB_REPO_LIST_IDS:
            for item in GitlabClient().project_merge_requests(project_id=project_id, scope='all', state='opened'):
                # text = item.get('description')[:40]

                if item.get('title').startswith('WIP'):
                    continue

                data['attachments'].append({
                    "title": '{} (#{})'.format(item.get('title'), item.get('id')),
                    "text": "<https://gitlab.com/{0}|{0}>".format(
                        item.get('references').get('full').split('!')[0],
                    ),
                    "title_link": item.get('web_url'),
                    "footer": 'criado por {}'.format(item.get('author').get('name')),
                    "footer_icon": item.get('author').get('avatar_url'),
                })

        return data


app = Chalice(app_name='connect')


@app.schedule(Cron(0, '12,17,20', '?', '*', 'MON-FRI', '*'))
def send_to_slack(event):
    Notification().send_to_slack()
