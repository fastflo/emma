"""
Emma MySql provider Table toolbar
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


class TableToolbar(gtk.Toolbar):
    """
    Emma MySql provider Table toolbar
    """
    def __init__(self, tab_table):
        super(TableToolbar, self).__init__()

        self.tab_table = tab_table

        self.set_icon_size(gtk.ICON_SIZE_MENU)
        self.refresh = gtk.ToolButton(gtk.STOCK_REFRESH)
        self.refresh.set_is_important(True)
        self.add(self.refresh)

        self.truncate = gtk.ToolButton(gtk.STOCK_CLEAR)
        self.truncate.set_label('Truncate')
        self.truncate.set_is_important(True)
        self.add(self.truncate)

        self.drop = gtk.ToolButton(gtk.STOCK_DELETE)
        self.drop.set_label('Drop')
        self.drop.set_is_important(True)
        self.add(self.drop)

        self.truncate.connect('clicked', self.tab_table.update)
        self.refresh.connect('clicked', self.tab_table.update)
