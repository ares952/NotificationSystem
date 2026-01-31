#!/usr/bin/env python3
import argparse
import sys
import os
import requests
# import notification_database


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


def send_notification(config, topic, title, text, tags, priority):
    if config['station']['publish_immediately']:
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


if __name__ == "__main__":
    import notification_config
    config = notification_config.load_config()
    config['station']['publish_immediately'] = False
    send_notification(config, "testing topic", "testing title", "testing text", "testing,tags", 5)
    sys.exit(0)
