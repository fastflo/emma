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


class PopUpDatabase(gtk.Menu):
    __gsignals__ = {
        'item-selected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,))
    }

    def __init__(self):
        super(PopUpDatabase, self).__init__()

        item = gtk.ImageMenuItem(gtk.STOCK_REFRESH)
        item.set_name('refresh_database')
        item.set_label('Refrest Database')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        item = gtk.ImageMenuItem(gtk.STOCK_DELETE)
        item.set_name('drop_database')
        item.set_label('Drop Database')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        self.append(gtk.SeparatorMenuItem())

        item = gtk.ImageMenuItem(gtk.STOCK_JUSTIFY_FILL)
        item.set_name('list_tables')
        item.set_label('List tables')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        self.append(gtk.SeparatorMenuItem())

        item = gtk.ImageMenuItem(gtk.STOCK_NEW)
        item.set_name('new_table')
        item.set_label('New Table')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        item = gtk.ImageMenuItem(gtk.STOCK_APPLY)
        item.set_name('check_tables')
        item.set_label('Check Tables')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        item = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
        item.set_name('repair_tables')
        item.set_label('Repair Tables')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        self.show_all()

    def activated(self, item):
        self.emit('item-selected', item)
        pass
