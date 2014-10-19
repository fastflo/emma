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


class TableIndexesPopUp(gtk.Menu):

    def __init__(self):
        super(TableIndexesPopUp, self).__init__()

        self.add = gtk.ImageMenuItem(gtk.STOCK_ADD)
        self.add.set_name('add')
        self.add.set_label('Add index')
        self.add.set_always_show_image(True)
        self.append(self.add)

        self.append(gtk.SeparatorMenuItem())

        self.edit = gtk.ImageMenuItem(gtk.STOCK_EDIT)
        self.edit.set_name('edit')
        self.edit.set_label('Edit index')
        self.edit.set_always_show_image(True)
        self.append(self.edit)

        self.append(gtk.SeparatorMenuItem())

        self.drop = gtk.ImageMenuItem(gtk.STOCK_DELETE)
        self.drop.set_name('drop')
        self.drop.set_label('Drop index')
        self.drop.set_always_show_image(True)
        self.append(self.drop)

        self.show_all()

    def popup(self, parent_menu_shell, parent_menu_item, func, button, activate_time, data=None):
        super(TableIndexesPopUp, self).popup(parent_menu_shell, parent_menu_item, func, button, activate_time, data)