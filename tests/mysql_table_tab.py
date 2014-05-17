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

import gtk
from emmalib.providers.mysql import MySqlHost
from emmalib.widgets.TabTable import TabTable


class Win(gtk.Window):

    def __init__(self):
        super(Win, self).__init__()
        self.set_position(gtk.WIN_POS_CENTER)
        self.resize(800, 600)
        self.connect('destroy', lambda *args: gtk.main_quit())
        self.host = None
        self.table = None
        self.db_connect()

        tt = TabTable(None, self.table)
        if tt:
            self.add(tt.get_ui())

        self.show_all()

    def db_connect(self):
        _db = 'test'
        _tb = 'aaa'
        self.host = MySqlHost(None, None, 'Localhost', 'localhost', 3306, 'root', 'root', '', 0)
        self.host.connect()
        self.host.use_db(_db)
        self.host.databases[_db].refresh()
        self.host.databases[_db].tables[_tb].refresh()
        self.table = self.host.databases[_db].tables[_tb]
        self.table.refresh()


w = Win()
gtk.main()