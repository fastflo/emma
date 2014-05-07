import time
from SQLiteIndex import SQLiteIndex


class SQLiteTable():
    def __init__(self, db, props):
        self.handle = db.handle
        self.host = db.host
        self.db = db
        self.props = props
        self.name = props[1]
        self.fields = {}
        self.field_order = []
        self.indexes = []
        self.expanded = False
        self.last_field_read = 0
        self.create_table = props[4]
        self.describe_headers = []
        self.is_table = props[0] == 'table'
        self.is_view = props[0] == 'view'

    def refresh(self, refresh_props=True):
        self.refresh_fields()
        self.refresh_indexes()

    def refresh_fields(self):
        self.fields = {}
        self.field_order = []
        self.host.query("PRAGMA table_info(`%s`)" % self.name, False, False)
        for h in self.host.handle.c.description:
            self.describe_headers.append(h[0])
        result = self.handle.store_result()
        for field in result.fetch_row(0):
            self.field_order.append(field[1])
            self.fields[field[1]] = field
        self.last_field_read = time.time()
        return

    def refresh_indexes(self):
        self.indexes = []
        res = self.host.query_dict("PRAGMA index_list(`%s`)" % self.name, append_to_log=False)
        for row in res['rows']:
            self.indexes.append(SQLiteIndex(row))

    def __str__(self):
        output = ""
        for h, p in zip(self.db.status_headers, self.props):
            output += "\t%-25.25s: %s\n" % (h, p)
        return output

    def get_create_table(self):
        return self.create_table

    def get_tree_row(self, field_name):
        return (self.fields[field_name][1],self.fields[field_name][2]),