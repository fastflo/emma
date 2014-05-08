class SQLiteField:
    def __init__(self, row):
        self.name = row['name']
        self.default = row['dflt_value']
        if row['notnull'] == 0:
            self.is_null = True
        else:
            self.is_null = False
        self.type = row['type']
