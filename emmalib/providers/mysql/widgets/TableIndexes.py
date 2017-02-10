"""
Emma MySql provider Indexes list
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

from emmalib.providers.mysql.widgets.TableIndexesPopUp import TableIndexesPopUp


class TableIndexes(gtk.ScrolledWindow):
    """
    Emma MySql provider Indexes list
    """
    def __init__(self, table):
        super(TableIndexes, self).__init__()

        self.table = table

        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.tv_indexes_model = gtk.ListStore(
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
        )
        self.tv_indexes = gtk.TreeView()
        self.tv_indexes.set_rules_hint(True)
        self.tv_indexes.set_model(self.tv_indexes_model)

        self.tv_indexes.connect("button-release-event", self.on_button_release)
        self.pop_up = TableIndexesPopUp()
        self.pop_up.add.connect('activate', self.on_add_activate)
        self.pop_up.edit.connect('activate', self.on_edit_activate)
        self.pop_up.drop.connect('activate', self.on_drop_activate)

        self.add(self.tv_indexes)

    @staticmethod
    def on_add_activate(item):
        """
        @param item:
        @return:
        """
        if not item:
            return

    @staticmethod
    def on_edit_activate(item):
        """
        @param item:
        @return:
        """
        if not item:
            return

    @staticmethod
    def on_drop_activate(item):
        """
        @param item:
        @return:
        """
        if not item:
            return

    def refresh(self):
        """
        Refresh list
        """
        for col in self.tv_indexes.get_columns():
            self.tv_indexes.remove_column(col)
        if self.tv_indexes_model:
            self.tv_indexes_model.clear()

        self.tv_indexes.append_column(gtk.TreeViewColumn("Name", gtk.CellRendererText(), text=0))
        self.tv_indexes.append_column(gtk.TreeViewColumn("Column", gtk.CellRendererText(), text=1))
        self.tv_indexes.append_column(gtk.TreeViewColumn("Unique", gtk.CellRendererText(), text=2))
        for ix in self.table.indexes:
            self.tv_indexes_model.append(
                (
                    ix.name,
                    ix.column,
                    ix.is_unique,
                )
            )

    def on_button_release(self, tv, event):
        """
        @param tv:
        @param event:
        @return:
        """
        if not tv or not event or not event.button == 3:
            return False
        self.pop_up.popup(None, None, None, event.button, event.time, tv)
