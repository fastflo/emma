from emmalib.providers.mysql.MySqlTable import *


class SQLiteTable(MySqlTable):
    def __init__(self, db, props):
        self.handle = db.handle
        self.host = db.host
        self.db = db
        self.props = props
        self.name = props[0]

        self.fields = {}
        self.field_order = []
        self.expanded = False
        self.last_field_read = 0
        self.create_table = ""
        self.describe_headers = []

    def __getstate__(self):
        d = dict(self.__dict__)
        for i in ["handle"]:
            del d[i]
        #print "table will pickle:", d
        return d

    def __getitem__(self, what):
        print "todo: props dict %r" % what
        return None

    def refresh(self, refresh_props=True):
        self.host.query("SELECT sql FROM sqlite_master WHERE type='table' and name='%s'" % self.name)
        result = self.handle.store_result()
        self.fields = {}
        self.field_order = []
        result = result.fetch_row(0)
        self.create_table = result[0][0]

        self.host.query("SELECT * FROM %s limit 1" % self.name)

        for field in self.host.handle.c.description:
            self.field_order.append(field[0])
            self.fields[field[0]] = field

        self.last_field_read = time.time()
        return

    def __str__(self):
        output = ""
        for h, p in zip(self.db.status_headers, self.props):
            output += "\t%-25.25s: %s\n" % (h, p)
        return output

    def get_create_table(self):
        if not self.host.query("SELECT sql FROM sqlite_master WHERE type='table' and name='%s'" % self.name): return
        result = self.handle.store_result()
        if not result:
            print "can't get create table for %s at %s and %s" % (self.name, self, self.handle)
            return ""
        result = result.fetch_row(0)
        self.create_table = result[0][0]
        return self.create_table
