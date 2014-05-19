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

from SQLiteIndex import SQLiteIndex
from SQLiteField import SQLiteField


class SQLiteTable:
    def __init__(self, db, props):
        self.handle = db.handle
        self.host = db.host
        self.db = db
        self.name = props[1]
        self.fields = []
        self.indexes = []
        self.expanded = False
        self.create_table = props[4]
        self.engine = ''
        self.comment = ''
        self.is_table = props[0] == 'table'
        self.is_view = props[0] == 'view'
        self.props = props

    def refresh(self):
        self.refresh_fields()
        self.refresh_indexes()

    def refresh_fields(self):
        self.fields = []
        res = self.host.query_dict("PRAGMA table_info(`%s`)" % self.name, append_to_log=False)
        for row in res['rows']:
            self.fields.append(SQLiteField(row))

    def refresh_indexes(self):
        self.indexes = []
        res = self.host.query_dict("PRAGMA index_list(`%s`)" % self.name, append_to_log=False)
        for row in res['rows']:
            ires = self.host.query_dict("PRAGMA index_info(`%s`)" % row['name'], append_to_log=False)
            irow = ires['rows'][0]
            row['column_name'] = irow['name']
            self.indexes.append(SQLiteIndex(row))

    def __str__(self):
        output = ""
        for h, p in zip(self.db.status_headers, self.props):
            output += "\t%-25.25s: %s\n" % (h, p)
        return output

    def get_create_table(self):
        return self.create_table

    def get_tree_row(self, field_name):
        return (self.fields[field_name].name, self.fields[field_name].type),

    def get_all_records(self):
        return self.host.query_dict("SELECT * FROM %s" % self.name, append_to_log=False)

    def get_table_properties_widget(self):
        return False

    def get_table_fields_widget(self):
        return False

    def get_table_indexes_widget(self):
        return False

    def get_table_toolbar(self):
        return False

    def get_table_status_string(self):
        return ''

    def on_toolbar_drop_table(self, *args):
        pass

    def on_toolbar_truncate_table(self, *args):
        pass