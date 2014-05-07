from SQLiteHost import SQLiteHost

host = SQLiteHost(None, None, '/home/nick/test.sqlite')
host.connect()

host.databases['dummydb'].refresh()
print host.databases['dummydb'].tables

table = host.databases['dummydb'].tables['aaa']
print "---------------------------"
print "Table:"
for p in table.__dict__:
    print p

table.refresh()

print "---------------------------"
print "Table fields order:"
for fo in table.field_order:
    print fo, ':'

print "---------------------------"
print "Table fields:"
for f in table.fields:
    print f, ':'
    print table.fields[f]

print "---------------------------"
print "Table indexes:"
for i in table.indexes:
    print i.__dict__