class SQLiteIndex:
    def __init__(self, row):
        print "SQLITE INDEX ROW = ", row
        self.name = row['name']
        if row['unique'] == 1:
            self.is_unique = True
        else:
            self.is_unique = False
        self.column = row['column_name']
