"""
Emma MySql provider test
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

from emmalib.providers.mysql.MySqlHost import MySqlHost

h = MySqlHost(None, None, 'Local', 'localhost', 3306, 'root', 'root', 'test', 1000)

h.connect()

if h.connected:
    print "Connected to:", h.get_connection_string()
else:
    print "Couldn't connect to:", h.get_connection_string()

h.refresh()

print h.databases['test'].tables
print h.databases['test'].refresh()
print h.databases['test'].tables
print h.databases['test'].tables['test'].fields
print h.databases['test'].tables['test'].refresh()
print h.databases['test'].tables['test'].fields

h.close()
