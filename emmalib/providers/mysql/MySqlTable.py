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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

import time
from MySqlIndex import MySqlIndex

class MySqlTable:
    def __init__(self, db, props, props_description):
        self.handle = db.handle
        self.host = db.host
        self.db = db
        self.props = props
        self.props_dict = dict(zip(props_description, props))
        self.name = props[0]
        self.fields = {}
        self.field_order = []
        self.indexes = []
        self.expanded = False
        self.last_field_read = 0
        self.create_table = ""
        self.describe_headers = []
        self.props_description = props_description
        self.engine = props[1]
        self.comment = props[17]
        self.is_table = False
        self.is_view = False
        if self.engine:
            self.is_table = True
        else:
            self.is_view = True

    def __getstate__(self):
        d = dict(self.__dict__)
        for i in ["handle"]:
            del d[i]
            #print "table will pickle:", d
        return d

    def __getitem__(self, what):
        try:
            return self.props_dict[what]
        except:
            pass
        print "property", what, "not found in table props:", self.props_dict

    def refresh(self, refresh_props=True):
        self.db.host.select_database(self.db)
        if refresh_props:
            self.refresh_properties()

        self.refres_fields()
        self.refresh_indexes()

    def refresh_properties(self):
        self.host.query("show table status like '%s'" % self.name)
        result = self.handle.store_result()
        rows = result.fetch_row(0)
        self.props = rows[0]
        self.props_dict = dict(zip(map(lambda v: v[0], result.describe()), rows[0]))
        self.name = self.props[0]

    def refres_fields(self):
        self.host.query("describe %s" % self.host.escape_table(self.name))
        result = self.handle.store_result()
        self.describe_headers = []
        self.fields = {}
        self.field_order = []
        if result is not None:
            for h in result.describe():
                self.describe_headers.append(h[0])
            for row in result.fetch_row(0):
                self.field_order.append(row[0])
                self.fields[row[0]] = row
        self.last_field_read = time.time()

    def refresh_indexes(self):
        self.host.query('SHOW INDEX FROM %s' % self.host.escape_table(self.name))
        result = self.handle.store_result()
        if result is not None:
            fields = []
            for h in result.describe():
                fields.append(h[0])
            print fields
            for row in result.fetch_row(0):
                self.indexes.append(MySqlIndex(dict(zip(fields, row))))

    def __str__(self):
        output = ""
        for h, p in zip(self.db.status_headers, self.props):
            output += "\t%-25.25s: %s\n" % (h, p)
        return output

    def get_create_table(self):
        if not self.create_table:
            self.db.host.select_database(self.db)
            self.host.query("show create table `%s`" % self.name)
            result = self.handle.store_result()
            if not result:
                print "can't get create table for %s at %s and %s" % (self.name, self, self.handle)
                return ""
            result = result.fetch_row(0)
            self.create_table = result[0][1]
        return self.create_table
