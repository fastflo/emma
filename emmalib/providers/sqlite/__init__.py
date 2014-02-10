from emmalib.providers import emma_registered_providers

try:
    import sqlite3
    from providers.sqlite.SQLiteHost import *
    from SQLiteDb import SQLiteDb
    from SQLiteHandle import SQLiteHandle
    from SQLiteHost import SQLiteHost
    from SQLiteResult import SQLiteResult
    from SQLiteTable import SQLiteTable
    emma_registered_providers.append('sqlite')
except:
    pass