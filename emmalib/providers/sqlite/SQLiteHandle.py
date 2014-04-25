from emmalib.providers.sqlite.SQLiteResult import SQLiteResult


class SQLiteHandle(object):
    def __init__(self, host, connection):
        self.host = host
        self.connection = connection
        self.connection.isolation_level = None
        self.c = self.connection.cursor()
        self.stored_result = False
        self.result = None

    def affected_rows(self):
        return 0  # todo

    def insert_id(self):
        return 0  # todo

    def execute(self, query):
        self.c.execute(query)
        self.stored_result = False

    def field_count(self):
        if self.c.description is None:
            return 0
        return len(self.c.description)

    def store_result(self):
        self.stored_result = True
        self.result = SQLiteResult(self.c.fetchall(), self.c.description)
        return self.result

    def close(self):
        self.connection.close()
