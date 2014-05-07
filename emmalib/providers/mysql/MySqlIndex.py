class MySqlIndex:
    def __init__(self, row):
        self.name = row['Key_name']
        if row['Non_unique'] == '0':
            self.is_unique = True
        else:
            self.is_unique = False
        self.column = row['Column_name']
