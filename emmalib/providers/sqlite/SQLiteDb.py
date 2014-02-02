from emmalib.providers.mysql.MySqlDb import MySqlDb
from emmalib.providers.sqlite.SQLiteTable import SQLiteTable


class SQLiteDb(MySqlDb):
    def __init__(self, host, name=None):
        self.handle = host.handle
        self.host = host
        self.charset = self.host.charset
        self.name = name
        self.expanded = False
        self.status_headers = []
        self.tables = {}

    def __getstate__(self):
        d = dict(self.__dict__)
        for i in ["handle"]:
            del d[i]
        #print "db will pickle:", d
        return d

    def refresh(self):
        if not self.host.query("SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name"): return
        new_tables = []
        result = self.handle.store_result()
        old = dict(zip(self.tables.keys(), range(len(self.tables))))
        for row in result.fetch_row(0):
            if not row[0] in old:
                #print "new table", row[0]
                self.tables[row[0]] = SQLiteTable(self, row)
                new_tables.append(row[0])
            else:
                del old[row[0]]
        for table in old:
            del self.tables[table]
        return new_tables

    def query(self, query, check_use=True, append_to_log=True):
        self.host.select_database(self)
        return self.host.query(query, check_use, append_to_log)