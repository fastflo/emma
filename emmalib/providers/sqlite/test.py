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

import sqlite3

conn = sqlite3.connect(database='/home/nick/test_database.sqlite')
print conn
cur = conn.cursor()
print cur.execute("SELECT * FROM sqlite_master ORDER BY name")
print cur.description
res = cur.fetchall()
for row in res:
    print row

    # from SQLiteHost import SQLiteHost
    #
    # host = SQLiteHost(None, None, '/home/nick/test.sqlite')
    # host.connect()
    #
    # host.databases['dummydb'].refresh()
    # print host.databases['dummydb'].tables
    #
    # table = host.databases['dummydb'].tables['aaa']
    # table.refresh()
    #
    # print "---------------------------"
    # print "Table:"
    # print table.__dict__
    #
    # print "---------------------------"
    # print "Table fields:"
    # for f in table.fields:
    #     print f.__dict__
    #
    # print "---------------------------"
    # print "Table indexes:"
    # for i in table.indexes:
    #     print i.__dict__
