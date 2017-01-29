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
from emmalib.EventsManager import EventsManager
import dialogs

from emmalib.Config import Config
from emmalib.KeyMap import KeyMap
from emmalib.providers.mysql import MySqlHost
from widgets import TabBlobView
from widgets.QueryTab import QueryTab


class Win(gtk.Window):

    def __init__(self):
        super(Win, self).__init__()
        self.mainwindow = self
        self.current_host = None
        self.set_position(gtk.WIN_POS_CENTER)
        self.resize(800, 600)
        self.connect('destroy', lambda *args: gtk.main_quit())
        self.host = None
        self.table = None
        self.db_connect()
        self.glade_path = '../emmalib/'
        self.key_map = KeyMap(self)
        self.config = Config(self)
        self.config.load()
        self.blob_view = TabBlobView(self)
        self.events = EventsManager(self)

        self.mainwindow = self
        self.main_notebook = type('Dummy', (object,), {})
        self.main_notebook.close_query_tab = self.dummy_close_query_tab
        self.main_notebook.add_query_tab = self.dummy_add_query_tab

        qt = QueryTab(self)
        qt.textview.get_buffer().set_text('SELECT * FROM test;')
        if qt:
            self.add(qt.get_ui())

        self.show_all()

    def assign_once(self, name, creator, *args):
        obj = creator(*args)
        return obj

    def dummy_close_query_tab(self):
        dialogs.alert('Test mode')

    def dummy_add_query_tab(self):
        dialogs.alert('Test mode')

    def db_connect(self):
        _db = 'test'
        _tb = 'test'
        self.host = MySqlHost(None, None, 'Localhost', 'localhost', 3306, 'root', 'root', '', 0)
        self.host.connect()
        self.host.use_db(_db)
        self.host.databases[_db].refresh()

        # print "DB:", _db, "TABLE:", _tb

        print len(self.host.databases[_db].tables)

        self.host.databases[_db].tables[_tb].refresh()

        self.table = self.host.databases[_db].tables[_tb]
        self.table.refresh()

        self.current_host = self.host


w = Win()
gtk.main()
