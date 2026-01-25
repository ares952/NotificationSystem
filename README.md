# NotificationSystem
Notification system scripts for ntfy.

# NTFY Configuration
The configuration file must be placed in one of the following paths:
- /etc directory
- /usr/local/etc directory
- /opt/etc directory
- ../etc from the path where the scripts are stored
- path where the scripts are stored

The files are attempted to be loaded in this particular order. If a file is found, it will be loaded and used. Please note, if more configurations exist, the data will be merged and the lates data are always preffered.

## Server
On the server, you need to install and configure NTFY. You can add new user by running the following command:
```docker exec -it ntfy ntfy user add <username>```
And type the password to console.

Modify the user permissions to the topic(s):
```docker exec -it ntfy ntfy access <username> my-topic* read-write```
In this case the new user has read and write access to all topic starting by my-topic.

You can check the publishing:
```curl -u 'username:password' -d "Testing topic" https://ntfy.example.com/my-topic-for-testing```

Configuration **ntfy** in **NotificationSystem.yaml** needs to be set accordingly.

## Database
The database does not need to be configured if the config['publishimmediately'] is set.

You need to install one of the following packages on the station to have access to mariadb server:
- python3-mysql.connector
- python3-mysqldb

You need to add the new user to the database (with access e.g. from localhost, from any LAN network IP range 192.168.1.0/24 and from any VPN network IP range 10.0.1.0/24):

```
create user 'notification_user'@'localhost' identified by 'notification_password';
grant all privileges on `notification%`.* to 'notification_user'@'localhost';
create user 'notification_user'@'192.168.1.%' identified by 'notification_password';
grant all privileges on `notification%`.* to 'notification_user'@'192.168.1.%';
create user 'notification_user'@'10.0.1.%' identified by 'notification_password';
grant all privileges on `notification%`.* to 'notification_user'@'10.0.1.%';
```
Configuration **database** in **NotificationSystem.yaml** needs to be set accordingly.

## Server station
The purpose of the server is to fetch notifications from the database and send them to the notification system within **fetchinterval** (s) timeout.

If the server station is enabled, it will attempt to create the database table and will collect data from the database each **fetchinterval** seconds and sent the request to notification server.

## Station
The station is responsible for sending notifications to the notification system.

It can be configured either to send the notification immediately or sends the notification to the database, where it is handled by the server notification system.

## Client
The client script provides easy-to-use interface for the notificartions. It allows you to send the notifications to the server.

### Usage

```
notification --help

notification --title='Title of the notification' --text='Text of the notification' --priority=3 -- tags='+1,warning,no_entry'
```

Text is expected in markdown format: https://docs.ntfy.sh/publish/#markdown-formatting

Message priority is described here: https://docs.ntfy.sh/publish/#message-priority

List of tags and emojis is available here: https://docs.ntfy.sh/publish/#tags-emojis

If text is not provided, it is not reported.

The default priority is 3 (medium).

If no tags are provided, non are reported.

Title is mandatory to be provided.


