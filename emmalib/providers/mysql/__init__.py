from emmalib.providers import emma_registered_providers

try:
    import _mysql
    import _mysql_exceptions
    from MySqlDb import MySqlDb
    from MySqlHost import MySqlHost
    from MySqlQueryTab import MySqlQueryTab
    from MySqlTable import MySqlTable
    emma_registered_providers.append('mysql')
except:
    pass


