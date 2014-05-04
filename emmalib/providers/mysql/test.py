from MySqlHost import MySqlHost
import MySqlDb
import MySqlTable


host = MySqlHost(None, None, 'Localhost', 'localhost', 3306, 'root', 'root', '', 0)
host.connect()
host._use_db('bohprod')

host.databases['bohprod'].refresh()
host.databases['bohprod'].tables['boh_users'].refresh()

print host.databases['bohprod'].tables['boh_users'].fields