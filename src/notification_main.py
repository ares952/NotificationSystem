#!/usr/bin/env python3
import argparse
import sys
import os
import requests
from notification_database import dbAccess
import string
import random


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


def post_notification(config, header):
    try:
        text = header.get('Text', '')
        header.pop('Text', None)
        topic = header.get('Topic', 'default')
        header.pop('Topic', None)
        response = requests.post(config['ntfy']['url']+"/"+topic,
                                 auth=(config['ntfy']['username'], config['ntfy']['password']),
                                 data=text.encode('utf-8'),
                                 headers=header)
        if response.status_code != 200:
            print(f"Failed to send notification: {response.status_code} {response.text}", flush=True)
            return 1
        else:
            return 0
    except Exception as e:
        print(f"Exception: {e}", flush=True)
        return 2


def send_notification(config, topic, title, text, tags, priority):
    headers = {
        'Title': f"{title}" if title is not None else "",
        'Priority': f"{priority}" if priority is not None else "3",
        'Tags': f"{tags}" if tags is not None else "",
        "Markdown": "yes",
        "Text": text,
        "Topic": topic
    }
    if config['station']['publish_immediately']:
        return post_notification(config, headers)
    else:
        with dbAccess(config['database']) as db:
            db.insert_notification(topic, headers)
        return 0


if __name__ == "__main__":
    attempt_to_get_topic()
    for prio in range(1, 6):
        validate_priority(prio)
    import notification_config
    config = notification_config.load_config()
    config['station']['publish_immediately'] = False
    random_table_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
    print(f"Using random table name: {random_table_name}")
    config['database']['table'] = random_table_name
    send_notification(config, "testing topic 1", "testing title 1", "testing text 1", "testing1,tag1", 1)
    send_notification(config, "testing topic 2", "testing title 2", "testing text 2", "testing2,tag2", 2)
    send_notification(config, "testing topic 3", "testing title 3", "testing text 3", "testing3,tag3", 3)
    send_notification(config, "testing topic 4", "testing title 4", "testing text 4", "testing4,tag4", 4)
    send_notification(config, "testing topic 5", "testing title 5", "testing text 5", "testing5,tag5", 5)

    with dbAccess(config['database']) as db:
        cursor = db.connection.cursor()
        while (item := db.get_next_notification()) is not None:
            print(item)
            db.delete_notification(item[0])

        cursor.execute(f"DROP TABLE {random_table_name};")
