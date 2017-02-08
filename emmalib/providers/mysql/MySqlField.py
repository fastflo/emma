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

field_types = [
    'TINYINT', 'SMALLINT', 'MEDIUMINT', 'INT', 'BIGINT',
    'DECIMAL', 'DOUBLE', 'FLOAT', 'REAL',
    'DATE', 'DATETIME', 'TIMESTAMP', 'TIME', 'YEAR',
    'CHAR', 'VARCHAR',
    'BLOB', 'TINYBLOB', 'MEDIUMBLOB', 'LONGBLOB',
    'TEXT', 'TINYTEXT', 'MEDIUMTEXT', 'LONGTEXT',
    'BINARY', 'VARBINARY',
    'ENUM', 'SET'
]
field_types_int = ['bit', 'bool', 'boolean', 'tinyint',
                   'smallint', 'mediumint', 'int', 'bigint', 'integer']
field_types_float = ['decimal', 'double', 'float', 'real']
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
        self.row = row
        # print row
        if len(row) > 0:
            self.name = row['Field']
            self.default = row['Default']
            if row['Null'] != 'NO':
                self.is_null = True
            else:
                self.is_null = False

            # print self.parse_type()
            _t_type, self.size, self.precission, self.unsigned, self.values = self.parse_type()
            self.type = _t_type.upper()
            self.type_string = self.row['Type']
            self.auto_increment = self.row['Extra'] == 'auto_increment'
            self.collation = row['Collation']
            self.comment = row['Comment']
        else:
            self.name = ''
            self.default = ''
            self.is_null = True
            self.type = 'INT'
            self.type_string = 'int(11)'
            self.size = 11
            self.precission = 0
            self.unsigned = False
            self.auto_increment = False
            self.collation = ''
            self.values = ''
            self.comment = ''

    def get_py_type(self):
        _t_type, _t_size, _t_scale, _t_unsigned, _t_values = self.parse_type()
        if _t_type in field_types_int:
            return long
        if _t_type in field_types_float:
            return float
        if _t_type in field_types_str:
            return str

    def parse_type(self):
        m = re.match(r'(.+)\((\d+),(\d+)\)\s(unsigned)', self.row['Type'])
        if m is not None:
            return m.group(1), int(m.group(2)), m.group(3), True, ''

        m = re.match(r'(.+)\((\d+),(\d+)\)', self.row['Type'])
        if m is not None:
            return m.group(1), int(m.group(2)), m.group(3), False, ''

        m = re.match(r'(.+)\((\d+)\)\s(unsigned)', self.row['Type'])
        if m is not None:
            return m.group(1), int(m.group(2)), 0, True, ''

        m = re.match(r'(.+)\((\d+)\)', self.row['Type'])
        if m is not None:
            return m.group(1), int(m.group(2)), 0, False, ''

        m = re.match(r'(.+)\((.+)\)', self.row['Type'])
        if m is not None:
            return m.group(1), 0, 0, False, m.group(2)

        m = re.match(r'(.+)', self.row['Type'])
        if m is not None:
            return m.group(1), 0, 0, False, ''
