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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

from MySqlField import MySqlField
from MySqlIndex import MySqlIndex


class MySqlTable:
    def __init__(self, db, props, props_description):
        self.handle = db.handle
        self.host = db.host
        self.db = db
        self.name = props[0]
        self.fields = []
        self.indexes = []
        self.expanded = False
        self.create_table = ""
        self.engine = props[1]
        self.comment = props[17]
        self.is_table = False
        self.is_view = False
        self.props = props

        self.props_dict = dict(zip(props_description, props))
        self.props_description = props_description

        if self.engine:
            self.is_table = True
        else:
            self.is_view = True

    def refresh(self, refresh_props=True):
        self.db.host.select_database(self.db)
        if refresh_props:
            self.refresh_properties()

        self.refresh_fields()
        self.refresh_indexes()

    def refresh_properties(self):
        self.host.query("show table status like '%s'" % self.name)
        result = self.handle.store_result()
        rows = result.fetch_row(0)
        self.props = rows[0]
        self.props_dict = dict(zip(map(lambda v: v[0], result.describe()), rows[0]))
        self.name = self.props[0]

    def refresh_fields(self):
        self.fields = []
        res = self.host.query_dict("describe %s" % self.host.escape_table(self.name))
        if not res:
            return
        for row in res['rows']:
            self.fields.append(MySqlField(row))

    def refresh_indexes(self):
        self.indexes = []
        res = self.host.query_dict('SHOW INDEX FROM %s' % self.host.escape_table(self.name))
        if not res:
            return
        for row in res['rows']:
            self.indexes.append(MySqlIndex(row))

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

    def get_tree_row(self, field_name):
        return (self.fields[field_name][0],self.fields[field_name][1]),

    def get_all_records(self):
        return self.host.query_dict("SELECT * FROM %s" % self.name, append_to_log=False)