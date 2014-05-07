# -*- coding: utf-8 -*-
# emma
#
# Copyright (C) 2006 Florian Schmidt (flo@fastflo.de)
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

from emmalib.providers.mysql.MySqlHost import *
from emmalib.providers.mysql.MySqlTable import *
from emmalib.providers.sqlite.SQLiteDb import SQLiteDb
from emmalib.providers.sqlite.SQLiteHandle import SQLiteHandle


class SQLiteHost(MySqlHost):
    def __init__(self, sql_log, msg_log, filename, *args):
        #MySqlHost.__init__(self, *args)
        self.sql_log, self.msg_log, self.filename = sql_log, msg_log, filename
        self.name = self.filename
        self.host = "localhost"
        self.user = os.getenv("USER")
        self.charset = "utf8"
        self.connected = False
        self.expanded = False
        self.handle = None
        self.current_db = None
        self.databases = {}
        self.processlist = None
        self.update_ui = None
        self.last_error = ""
        self.query_time = 0

    def __getstate__(self):
        d = dict(self.__dict__)
        for i in ["sql_log", "msg_log", "handle", "processlist", "update_ui", "update_ui_args"]:
            del d[i]
        #print "host will pickle:", d
        return d

    def get_connection_string(self):
        return "::sqlite::"

    def set_update_ui(self, update_ui, *args):
        self.update_ui = update_ui
        self.update_ui_args = args

    def connect(self):
        try:
            self.handle = SQLiteHandle(self, sqlite3.connect(self.filename))
        except:
            self.connected = False
            if self.msg_log:
                self.msg_log("%s: %s" % (sys.exc_type, sys.exc_value))
            return
        self.current_db = SQLiteDb(self, "dummydb")
        self.databases = {"dummydb": self.current_db}
        self.connected = True
        self.refresh()

    def ping(self):
        return True

    def close(self):
        self.databases = {}
        self.processlist = None
        if self.handle:
            self.handle.close()
            self.handle = None
        self.connected = False
        if self.update_ui:
            self.update_ui(self, *self.update_ui_args)

    def query(self, query, check_use=True, append_to_log=True, encoding=None):
        if not self.handle:
            if self.msg_log:
                self.msg_log("not connected! can't execute %s, %s, %s" % (query, str(self.handle), str(self)))
            return
        if append_to_log:
            if self.sql_log:
                self.sql_log(query)
        try:
            self.query_time = 0
            start = time.time()
            if encoding:
                query = query.encode(encoding, "ignore")
            print "executing query (encoding: %s): %r" % (encoding, query)
            self.handle.execute(query)
            self.query_time = time.time() - start
        except:
            print "error executing query:\n%s" % traceback.format_exc()
            s = str(sys.exc_value)
            self.last_error = s
            if self.msg_log:
                self.msg_log(s)
            return False

        return True

    def use_db(self, name, do_query=True):
        pass

    def select_database(self, db):
        pass

    def refresh(self):
        pass

    def refresh_processlist(self):
        pass

    def insert_id(self):
        raise Exception("todo")  # return self.handle.insert_id()

    def escape(self, s):
        print "todo: sqlite escape!"
        return repr(s)[1:-1]

    def escape_field(self, field):
        print "todo: sqlite escape_field!"
        return field

    def escape_table(self, table):
        return table