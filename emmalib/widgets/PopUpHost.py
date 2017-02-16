"""
PopUpHost
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

import gtk
import gobject


class PopUpHost(gtk.Menu):
    """
    PopUpHost
    """
    __gsignals__ = {
        'item-selected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,))
    }

    def __init__(self):
        super(PopUpHost, self).__init__()

        self.menu_refresh_host = gtk.ImageMenuItem(gtk.STOCK_REFRESH)
        self.menu_refresh_host.set_name('refresh_host')
        self.menu_refresh_host.set_label('Refrest host')
        self.menu_refresh_host.set_always_show_image(True)
        self.menu_refresh_host.connect('activate', self.activated)
        self.append(self.menu_refresh_host)

        self.menu_modify_connection = gtk.ImageMenuItem(gtk.STOCK_EDIT)
        self.menu_modify_connection.set_name('modify_connection')
        self.menu_modify_connection.set_label('Modify Connection')
        self.menu_modify_connection.set_always_show_image(True)
        self.menu_modify_connection.connect('activate', self.activated)
        self.append(self.menu_modify_connection)

        self.menu_delete_connection = gtk.ImageMenuItem(gtk.STOCK_DELETE)
        self.menu_delete_connection.set_name('delete_connection')
        self.menu_delete_connection.set_label('Delete Connection')
        self.menu_delete_connection.set_always_show_image(True)
        self.menu_delete_connection.connect('activate', self.activated)
        self.append(self.menu_delete_connection)

        item = gtk.SeparatorMenuItem()
        self.append(item)

        self.menu_new_connection = gtk.ImageMenuItem(gtk.STOCK_NEW)
        self.menu_new_connection.set_name('new_connection')
        self.menu_new_connection.set_label('New Connection')
        self.menu_new_connection.set_always_show_image(True)
        self.menu_new_connection.connect('activate', self.activated)
        self.append(self.menu_new_connection)

        self.menu_new_database = gtk.ImageMenuItem(gtk.STOCK_NEW)
        self.menu_new_database.set_name('new_database')
        self.menu_new_database.set_label('New Database')
        self.menu_new_database.set_always_show_image(True)
        self.menu_new_database.connect('activate', self.activated)
        self.append(self.menu_new_database)

        item = gtk.SeparatorMenuItem()
        self.append(item)

        self.menu_show_processes = gtk.ImageMenuItem(gtk.STOCK_INFO)
        self.menu_show_processes.set_name('show_processes')
        self.menu_show_processes.set_label('Show Processes')
        self.menu_show_processes.set_always_show_image(True)
        self.menu_show_processes.connect('activate', self.activated)
        self.append(self.menu_show_processes)

        self.show_all()

    def activated(self, item):
        """
        @param item:
        """
        self.emit('item-selected', item)
