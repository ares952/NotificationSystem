#!/usr/bin/env python3
import argparse
import sys
import os
import notification_config
import requests


def attempt_to_get_topic():
    executed_name = os.path.basename(sys.argv[0])
    real_script_name_with_ext = os.path.basename(os.path.realpath(sys.argv[0]))
    real_script_name = os.path.splitext(real_script_name_with_ext)[0]
    if executed_name != real_script_name and executed_name.startswith(real_script_name):
        if len(executed_name) > len(real_script_name) and executed_name[len(real_script_name)] in ['_', '-']:
            suffix = executed_name[len(real_script_name) + 1:]
            if suffix:
                return suffix.removesuffix('.py')
    return None


def validate_priority(arg_value):
    try:
        int_value = int(arg_value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{arg_value}' is not a number")
    if not (1 <= int_value <= 5):
        raise argparse.ArgumentTypeError(f"'{int_value}' must be in range 1-5")

    return int_value


parser = argparse.ArgumentParser(description="Notification system")
parser.add_argument("text", type=str, help="Formatted text of the notification")
parser.add_argument("--topic", type=str, help="Topic where the notification shall be sent to")
parser.add_argument("--title", type=str, help="Title of the notification")
parser.add_argument("--priority", type=validate_priority, default=3, help="Priority of the notification (default 3)")
parser.add_argument("--tags", type=str, help="Comma separated tags of the notification")
args = parser.parse_args()

topic = attempt_to_get_topic()
if topic is None:
    if args.topic is None:
        raise argparse.ArgumentTypeError("Topic is not defined!")
    topic = args.topic

config = notification_config.load_config()


def send_notification(topic, title, text, tags, priority):
    headers = {
        'Title': f"{title}" if title is not None else "",
        'Priority': f"{priority}" if priority is not None else "3",
        'Tags': f"{tags}" if tags is not None else "",
        "Markdown": "yes"
    }
    try:
        # print(f"{text}", flush=True)
        response = requests.post(config['ntfy']['url']+"/"+topic,
                                 auth=(config['ntfy']['username'], config['ntfy']['password']),
                                 data=text.encode('utf-8'),
                                 headers=headers)
        if response.status_code != 200:
            print(f"Failed to send notification: {response.status_code} {response.text}", flush=True)
        else:
            pass
    except Exception as e:
        print(f"Exception: {e}", flush=True)


if config['station']['publish_immediately']:
    send_notification(topic, args.title, args.text, args.tags, args.priority)
