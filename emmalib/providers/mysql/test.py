from MySqlHost import MySqlHost
import MySqlDb
import MySqlTable


host = MySqlHost(None, None, 'Localhost', 'localhost', 3306, 'root', 'root', '', 0)
host.connect()
host.use_db('bohprod')

host.databases['bohprod'].refresh()
host.databases['bohprod'].tables['boh_users'].refresh()

table = host.databases['bohprod'].tables['boh_users']
print "---------------------------"
print "Table:"
for p in table.__dict__:
    print p

print "---------------------------"
print "Table fields:"
for f in table.fields:
    print f, ':'
    print table.fields[f]

print "---------------------------"
print "Table indexes:"
for i in host.databases['bohprod'].tables['boh_users'].indexes:
    print i.__dict__