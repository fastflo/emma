import time
from SQLiteIndex import SQLiteIndex


class SQLiteTable():
    def __init__(self, db, props, props_description):
        #MySqlTable.__init__(self, db, props, props_description)
        self.handle = db.handle
        self.host = db.host
        self.db = db
        self.props = props
        self.name = props[0]
        self.fields = {}
        self.field_order = []
        self.indexes = []
        self.expanded = False
        self.last_field_read = 0
        self.create_table = ""
        self.describe_headers = []
        self.is_table = True
        self.is_view = False

    def refresh(self, refresh_props=True):
        self.host.query("SELECT sql FROM sqlite_master WHERE type='table' and name='%s'" % self.name)
        result = self.handle.store_result()
        self.fields = {}
        self.field_order = []
        result = result.fetch_row(0)
        self.create_table = result[0][0]
        self.refresh_fields()
        self.refresh_indexes()

    def refresh_fields(self):
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
        self.host.query("PRAGMA index_list(`%s`)" % self.name, False, False)
        result = self.handle.store_result()
        if result is not None:
            fields = []
            for h in self.host.handle.c.description:
                fields.append(h[0])
            for row in result.fetch_row(0):
                self.indexes.append(SQLiteIndex(dict(zip(fields, row))))

    def __str__(self):
        output = ""
        for h, p in zip(self.db.status_headers, self.props):
            output += "\t%-25.25s: %s\n" % (h, p)
        return output

    def get_create_table(self):
        if not self.host.query("SELECT sql FROM sqlite_master WHERE type='table' and name='%s'" % self.name):
            return
        result = self.handle.store_result()
        if not result:
            print "can't get create table for %s at %s and %s" % (self.name, self, self.handle)
            return ""
        result = result.fetch_row(0)
        self.create_table = result[0][0]
        return self.create_table

    def get_tree_row(self, field_name):
        return (self.fields[field_name][1],self.fields[field_name][2]),