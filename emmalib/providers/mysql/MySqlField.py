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

import re

field_types_int = ['bit', 'bool', 'boolean', 'tinyint', 'smallint', 'mediumint', 'int', 'bigint', 'integer']
field_types_float = ['decimal', 'double', 'float']
field_types_str = [
    'date', 'datetime', 'timestamp', 'time', 'year',
    'char', 'varchar',
    'blob', 'tinyblob', 'mediumblob', 'longblob',
    'text', 'tinytext', 'mediumtext', 'longtext',
    'binary', 'varbinary',
    'enum', 'set'
]


class MySqlField:
    def __init__(self, row):
        self.name = row['Field']
        self.default = row['Default']
        if row['Null'] != 'NO':
            self.is_null = True
        else:
            self.is_null = False
        self.type = row['Type']

        self._t_type, self._t_size, self._t_scale = self.parse_type()

    def get_py_type(self):
        if self._t_type in field_types_int:
            return long
        if self._t_type in field_types_float:
            return float
        if self._t_type in field_types_str:
            return str

    def parse_type(self):
        m = re.match(r'(.+)\((\d+)\,(\d+)\)', self.type)
        if m is not None:
            return m.group(1), int(m.group(2)), m.group(3)

        m = re.match(r'(.+)\((\d+)\)', self.type)
        if m is not None:
            return m.group(1), int(m.group(2)), 0

        m = re.match(r'(.+)', self.type)
        if m is not None:
            return m.group(1), 0, 0