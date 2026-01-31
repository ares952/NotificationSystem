#!/usr/bin/env python3
from notification_database import dbAccess
import notification_config
import notification_main
import time
import json


if __name__ == "__main__":
    config = notification_config.load_config()
    config['station']['publish_immediately'] = True
    fetch_counter = 0
    config_reload_counter = 0
    while True:
        fetch_counter += 1
        print(f"Fetch cycle {fetch_counter}.", flush=True)
        with dbAccess(config['database']) as db:
            cursor = db.connection.cursor()
            while (item := db.get_next_notification()) is not None:
                print(item, flush=True)
                if item[2] >= config['server']['min_priority']:
                    result = notification_main.post_notification(config, json.loads(item[3]))
                else:
                    print("Skipping notification due to low priority.", flush=True)
                    result = 0
                if result == 0:
                    db.delete_notification(item[0])
                    time.sleep(config['server']['delay_interval'])  # brief pause between notifications

        time.sleep(config['server']['fetch_interval'])

        config_reload_counter += 1
        if (config['server']['config_reload'] is not None) and (config_reload_counter >= config['server']['config_reload']):
            config = notification_config.load_config()
            config['station']['publish_immediately'] = True
            print("Configuration file reloaded.", flush=True)
            config_reload_counter = 0
