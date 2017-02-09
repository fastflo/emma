"""
MySQL field class handler
"""
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

FIELD_TYPES = [
    'TINYINT', 'SMALLINT', 'MEDIUMINT', 'INT', 'BIGINT',
    'DECIMAL', 'DOUBLE', 'FLOAT', 'REAL',
    'DATE', 'DATETIME', 'TIMESTAMP', 'TIME', 'YEAR',
    'CHAR', 'VARCHAR',
    'BLOB', 'TINYBLOB', 'MEDIUMBLOB', 'LONGBLOB',
    'TEXT', 'TINYTEXT', 'MEDIUMTEXT', 'LONGTEXT',
    'BINARY', 'VARBINARY',
    'ENUM', 'SET'
]
FIELD_TYPES_INT = ['bit', 'bool', 'boolean', 'tinyint',
                   'smallint', 'mediumint', 'int', 'bigint', 'integer']
FIELD_TYPES_FLOAT = ['decimal', 'double', 'float', 'real']
FIELD_TYPES_STR = [
    'date', 'datetime', 'timestamp', 'time', 'year',
    'char', 'varchar',
    'blob', 'tinyblob', 'mediumblob', 'longblob',
    'text', 'tinytext', 'mediumtext', 'longtext',
    'binary', 'varbinary',
    'enum', 'set'
]


class MySqlField(object):
    """
    Class which wraps MySQL field logic
    """
    def __init__(self, row):
        self.row = row
        # print row
        if len(row) > 0:
            self.name = row['Field']
            self.default = row['Default']
            self.is_null = row['Null'] != 'NO'

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
        """
        Get Python type from MySQL type
        :return: type
        """
        _t_type = self.parse_type()[:1]
        if _t_type in FIELD_TYPES_INT:
            return long
        if _t_type in FIELD_TYPES_FLOAT:
            return float
        if _t_type in FIELD_TYPES_STR:
            return str

    def parse_type(self):
        """
        :return: ()
        """
        match = re.match(r'(.+)\((\d+),(\d+)\)\s(unsigned)', self.row['Type'])
        if match is not None:
            return match.group(1), int(match.group(2)), match.group(3), True, ''

        match = re.match(r'(.+)\((\d+),(\d+)\)', self.row['Type'])
        if match is not None:
            return match.group(1), int(match.group(2)), match.group(3), False, ''

        match = re.match(r'(.+)\((\d+)\)\s(unsigned)', self.row['Type'])
        if match is not None:
            return match.group(1), int(match.group(2)), 0, True, ''

        match = re.match(r'(.+)\((\d+)\)', self.row['Type'])
        if match is not None:
            return match.group(1), int(match.group(2)), 0, False, ''

        match = re.match(r'(.+)\((.+)\)', self.row['Type'])
        if match is not None:
            return match.group(1), 0, 0, False, match.group(2)

        match = re.match(r'(.+)', self.row['Type'])
        if match is not None:
            return match.group(1), 0, 0, False, ''
