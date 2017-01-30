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

from emmalib.providers.sqlite.SQLiteTable import SQLiteTable


class SQLiteDb:
    def __init__(self, host, name=None):
        self.handle = host.handle
        self.host = host
        self.charset = self.host.charset
        self.name = name
        self.expanded = False
        self.status_headers = []
        self.tables = {}

    def refresh(self):
        if not self.host.query(
                "SELECT * FROM sqlite_master WHERE type='table' OR type='view' ORDER BY name"):
            return
        new_tables = []
        result = self.handle.store_result()
        old = dict(zip(self.tables.keys(), range(len(self.tables))))
        for row in result.fetch_row(0):
            if not row[0] in old:
                self.tables[row[1]] = SQLiteTable(self, row)
                new_tables.append(row[1])
            else:
                del old[row[0]]
        for table in old:
            del self.tables[table]
        return new_tables

    def query(self, query, check_use=True, append_to_log=True):
        self.host.select_database(self)
        return self.host.query(query, check_use, append_to_log)