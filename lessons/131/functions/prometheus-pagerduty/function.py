import urllib3
import json


url = 'https://events.pagerduty.com/v2/enqueue'
routing_key = 'a55a38b56cf740secret7e500b68'

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
    event_action = str()
    if alarm['state'] == 'firing':
        event_action = 'trigger'
    elif alarm['state'] == 'resolved':
        event_action = 'resolve'

    return {
        "routing_key": routing_key,
        "event_action": event_action,
        "dedup_key": alarm['timestamp'],
        "payload": {
            "source": alarm['instance'],
            "summary": alarm['summary'],
            "custom_details": {
                "Environment": environment,
                "Description": alarm['description']
            },
            "severity": alarm['severity']
        }
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
