import sys
import notification_config

# Module Imports
try:
    import MySQLdb as mysql
    print("Using MySQLdb from mysqlclient")
except ModuleNotFoundError:
    print("No mysql module available")
    sys.exit(1)


class dbAccess:
    connection = None
    cursor = None
    config = None
    table_name = None

    def __init__(self, config, table_name="notifications"):
        self.config = config
        self.table_name = table_name
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
                user=config['database']['username'],
                password=config['database']['password'],
                host=config['database']['server'],
                port=config['database']['port'],
                database=config['database']['database'],
                collation='utf8mb4_unicode_ci'
            )
            self.cursor = self.connection.cursor()
            self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.table_name}
                                (id INT PRIMARY KEY AUTO_INCREMENT,
                                 topic VARCHAR(255),
                                 title VARCHAR(255),
                                 priority TINYINT,
                                 tags VARCHAR(255),
                                 message varCHAR(2048),
                                 reported_time DATETIME DEFAULT CURRENT_TIMESTAMP
                                );""")
        except mysql.Error as e:
            print(f"Error connecting to SQL platform: {e}")
            sys.exit(1)

    def insert_notification(self, topic, title, priority, tags, message):
        sql = f"INSERT INTO {self.table_name} (topic, title, priority, tags, message) VALUES (%s, %s, %s, %s, %s);"
        values = (topic, title, priority, tags, message)
        self.cursor.execute(sql, values)

    def get_next_notification(self):
        sql = f"SELECT * FROM {self.table_name} ORDER BY priority DESC, ID ASC LIMIT 1;"
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def delete_notification(self, notification_id):
        sql = f"DELETE FROM {self.table_name} WHERE id = %s;"
        values = (notification_id,)
        self.cursor.execute(sql, values)

    def commit(self):
        self.connection.commit()

    def close(self):
        cursor.close()
        self.connection.close()


if __name__ == "__main__":
    import sys
    config = notification_config.load_config()
    with dbAccess(config, "testing_table") as db:
        cursor = db.connection.cursor()
        db.insert_notification('test-topic', 'Test Title 1', 3, 'tag1,tag2', 'This is a test notification message.')
        db.insert_notification('test-topic2', 'Test Title 2', 5, 'tag3,tag4', 'This is another test notification message.')
        db.commit()

        cursor.execute(f"SELECT * FROM {db.table_name};")
        rows = cursor.fetchall()
        for row in rows:
            print(row)

        while (item := db.get_next_notification()) is not None:
            print(item)
            db.delete_notification(item[0])

        cursor.execute(f"DROP TABLE {db.table_name};")

    sys.exit(0)
