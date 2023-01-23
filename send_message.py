import logging
import requests
from requests.structures import CaseInsensitiveDict
import datetime
import json
import os


def send_message (path, status_code):
    data = """
		{
	"blocks": [
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "WEB ERROR STATUS_CODE"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Please, contact <@UMQ9N79RN> if you need help.* :thinking_face:"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "PATH"
			},
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": "Click Me",
					"emoji": true
				},
				"value": "click_me_123",
				"url": "PATH",
				"action_id": "button-action"
			}
		}
	]
}
	"""
    data = data.replace('PATH', path).replace('STATUS_CODE', status_code)
    url = os.environ['WEBHOOK_URI']

    headers = CaseInsensitiveDict()
    headers["Content-type"] = "application/json"

    resp = requests.post(url, headers=headers, data=data)
    print (resp)

def passed_message():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = """
		{
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "All checks passed"
			}
		}
	]
}
	"""
    url = os.environ['WEBHOOK_URI']

    headers = CaseInsensitiveDict()
    headers["Content-type"] = "application/json"

    resp = requests.post(url, headers=headers, data=data)
    print (resp)
    
def report(attachments):
    print (attachments)
    data = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Daily Report"
                }
            }
        ],
        "attachments": attachments
    }
    
    url = os.environ['WEBHOOK_URI']
    headers = CaseInsensitiveDict()
    headers["Content-type"] = "application/json"

    resp = requests.post(url, headers=headers, data=json.dumps(data))
    print(resp)
    