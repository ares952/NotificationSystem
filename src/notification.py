#!/usr/bin/env python3
import argparse
import notification_config
import notification_main


parser = argparse.ArgumentParser(description="Notification system")
parser.add_argument("text", type=str, help="Formatted text of the notification")
parser.add_argument("--topic", type=str, help="Topic where the notification shall be sent to")
parser.add_argument("--title", type=str, help="Title of the notification")
parser.add_argument("--priority", type=notification_main.validate_priority,
                    default=3, help="Priority of the notification (default 3)")
parser.add_argument("--tags", type=str, help="Comma separated tags of the notification")
args = parser.parse_args()

topic = notification_main.attempt_to_get_topic()
if topic is None:
    if args.topic is None:
        raise argparse.ArgumentTypeError("Topic is not defined!")
    topic = args.topic

config = notification_config.load_config()

notification_main.send_notification(config, topic, args.title, args.text, args.tags, args.priority)
