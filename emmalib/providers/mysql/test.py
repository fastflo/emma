# -*- coding: utf-8 -*-
# emma
#
# Copyright (C) 2006 Florian Schmidt (flo@fastflo.de)
#               2014 Nickolay Karnaukhov (mr.electronick@gmail.com)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA	 02110-1301 USA


# import MySQLdb
#
# conn = MySQLdb.connect(host='localhost', user='root', passwd='root')
# print conn
# """@type cur: MySQLdb.cursors.Cursor"""
# cur = conn.cursor()
# print cur.execute('USE test; SHOW TABLE STATUS;')
# res = cur.fetchall()
# print res
# print cur.nextset()
# for row in cur.description:
#     print row
# res = cur.fetchall()
# for row in res:
#     print row
# print cur.nextset()


# _db = 'test'
# _tb = 'aaa'
#
# from MySqlHost import MySqlHost
#
# host = MySqlHost(None, None, 'Localhost', 'localhost', 3306, 'root', 'root', '', 0)
# host.connect()
# host.use_db(_db)
#
# res = host.query_dict('SELECT * FROM boh_users')
# for t in res['types']:
#     print t
# for row in res['cols']:
#     print row
# for row in res['rows']:
#     print row


# host.databases[_db].refresh()
# host.databases[_db].tables[_tb].refresh()
#
# table = host.databases[_db].tables[_tb]
# print "---------------------------"
# print "Table:"
# for p in table.__dict__:
#     print p.ljust(20), table.__dict__[p]

# print "---------------------------"
# print "Table fields:"
# for f in table.fields:
#     print f.name.ljust(24), \
#         f.type.ljust(16), \
#         str(f.get_py_type()).ljust(20)

# print "---------------------------"
# print "Table indexes:"
# for i in table.indexes:
#     print i.__dict__