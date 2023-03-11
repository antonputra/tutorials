import urllib3
import json


url = 'https://hooks.slack.com/services/T01EJNXE7KR/B0492S75QQ1/4gtoPsecretlM3PCW'
http = urllib3.PoolManager()


def get_alarm_attributes(alert):
    alarm = dict()

    alarm['name'] = alert['labels']['alertname']
    alarm['summary'] = alert['annotations']['summary']
    alarm['description'] = alert['annotations']['description']
    alarm['instance'] = alert['labels']['instance']
    alarm['state'] = alert['status']
    alarm['severity'] = alert['labels']['severity']
    alarm['timestamp'] = alert['startsAt']

    return alarm


def generate_alarm_message(alarm, environment):
    text = str()
    if alarm['state'] == 'firing':
        text = ':red_circle: Alarm: ' + alarm['name']
    elif alarm['state'] == 'resolved':
        text = ':large_green_circle: Alarm: ' + alarm['name'] + ' was resolved'

    return {
        "type": "home",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": text,
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*" + alarm['summary'] + "*"
                },
                "block_id": "summary"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "_" + alarm['description'] + "_"
                },
                "block_id": "description"
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "Instance: *" + alarm['instance'] + "*"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "Severity: *" + alarm['severity'] + "*"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "Environment: *" + environment + "*"
                    }
                ]
            }
        ]
    }


def lambda_handler(event, context):
    sns_message = json.loads(event['Records'][0]['Sns']['Message'])
    sns_attributes = event['Records'][0]['Sns']['MessageAttributes']

    environment = sns_attributes['value']['Value']

    for alert in sns_message['alerts']:
        alarm = get_alarm_attributes(alert)
        payload = generate_alarm_message(alarm, environment)
        encoded_payload = json.dumps(payload).encode('utf-8')
        resp = http.request('POST', url, body=encoded_payload)

        print(
            {
                "message": payload,
                "status_code": resp.status,
                "response": resp.data,
            }
        )
