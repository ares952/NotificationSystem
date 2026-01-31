import sys
import notification_config
import json

# Module Imports
try:
    import MySQLdb as mysql
    # print("Using MySQLdb from mysqlclient")
except ModuleNotFoundError:
    # print("No mysql module available")
    sys.exit(1)


class dbAccess:
    connection = None
    cursor = None
    config = None

    def __init__(self, config):
        self.config = config
        self.open()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            print(f"Exception caught: {exc_type.__name__} - {exc_value}")
            return True
        self.close()
        return False

    def open(self):
        # Connect to MariaDB Platform
        try:
            self.connection = mysql.connect(
                user=self.config['username'],
                password=self.config['password'],
                host=self.config['server'],
                port=self.config['port'],
                database=self.config['database'],
                collation='utf8mb4_unicode_ci'
            )
            self.cursor = self.connection.cursor()
            self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.config['table']}
                                (id INT PRIMARY KEY AUTO_INCREMENT,
                                 topic VARCHAR(255),
                                 priority TINYINT,
                                 message varCHAR(8192),
                                 reported_time DATETIME DEFAULT CURRENT_TIMESTAMP
                                );""")
        except mysql.Error as e:
            print(f"Error connecting to SQL platform: {e}")
            sys.exit(1)

    def insert_notification(self, topic, message, priority=None):
        if priority is None:
            if isinstance(message, dict):
                priority = message.get('Priority', 3)
            else:
                priority = 3
        message = json.dumps(message)
        sql = f"INSERT INTO {self.config['table']} (topic, priority, message) VALUES (%s, %s, %s);"
        values = (topic, priority, message)
        self.cursor.execute(sql, values)

    def get_next_notification(self):
        sql = f"SELECT * FROM {self.config['table']} ORDER BY priority DESC, reported_time ASC, id ASC LIMIT 1;"
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def delete_notification(self, notification_id):
        sql = f"DELETE FROM {self.config['table']} WHERE id = %s;"
        values = (notification_id,)
        self.cursor.execute(sql, values)

    def commit(self):
        self.connection.commit()

    def close(self):
        self.commit()
        self.cursor.close()
        self.connection.close()


if __name__ == "__main__":
    config = notification_config.load_config()
    config['database']['table'] = 'notification_testing_table'
    with dbAccess(config['database']) as db:
        cursor = db.connection.cursor()
        db.insert_notification('test-topic', 'This is a test notification message.')
        db.insert_notification('test-topic2', 'This is another test notification message.', 5)
        header = {
            'Title': "Test Title",
            'Priority': "4",
            'Tags': "tag1,tag2",
            "Markdown": "yes"
        }
        db.insert_notification('test-topic2', header)
        db.commit()

        cursor.execute(f"SELECT * FROM {config['database']['table']};")
        rows = cursor.fetchall()
        for row in rows:
            print(row)

        while (item := db.get_next_notification()) is not None:
            print(item)
            db.delete_notification(item[0])

        cursor.execute(f"DROP TABLE {config['database']['table']};")
