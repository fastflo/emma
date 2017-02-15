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

import gc

from BaseTab import BaseTab
from ResultView import ResultView


class TabTable(BaseTab):
    """
    @param emma: Emma
    """
    def __init__(self, emma, table):
        super(TabTable, self).__init__()

        self.notebook = gtk.Notebook()
        self.tab_label.set_text('Table: %s' % table.name)

        self.emma = emma
        self.table = table
        self.status_text = gtk.Label()

        self.table.on('changed', self.table_changed)

        #
        #   DATA
        #
        self.data_view = ResultView()
        self.data_view.enable_sorting = True
        self.notebook.append_page(self.data_view, gtk.Label('Data'))

        #
        #   FIELDS
        #
        self.table_fields = table.get_table_fields_widget()
        if self.table_fields:
            self.notebook.append_page(self.table_fields, gtk.Label('Fields'))

        #
        #   INDEXES
        #
        if self.table.is_table:
            self.table_indexes = table.get_table_indexes_widget()
            if self.table_indexes:
                self.notebook.append_page(self.table_indexes, gtk.Label('Indexes'))

        #
        #   PROPERTIES
        #
        self.table_properties = table.get_table_properties_widget()
        if self.table_properties:
            self.notebook.append_page(self.table_properties, gtk.Label('Properties'))

        #
        #   CREATE TABLE/VIEW SQL
        #
        sql_create_tab = gtk.ScrolledWindow()
        sql_create_tab.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.table_textview = gtk.TextView()
        sql_create_tab.add(self.table_textview)
        self.notebook.append_page(sql_create_tab, gtk.Label('SQL: Create'))

        self.load()

        self.notebook.set_current_page(0)

        vbox = gtk.VBox()
        self.toolbar = table.get_table_toolbar(self)
        if self.toolbar:
            vbox.pack_start(self.toolbar, False, True)
        vbox.pack_start(self.notebook, True, True)
        vbox.pack_end(self.create_statusbar(), False, True)
        vbox.show_all()

        self.table_data_result = {}

        self.ui = vbox

    def create_statusbar(self):
        """
        @return: gtk.HBox
        """
        hbox = gtk.HBox()
        hbox.pack_start(self.status_text, False, True)
        return hbox

    def update(self, *_):
        """
        @param _:
        """
        self.table.refresh()
        self.load()

    def load(self):
        """
        Load
        """
        self.table_data_result = self.table.get_all_records()
        self.data_view.load_data(self.table_data_result)
        self.status_text.set_text(self.table.get_table_status_string())
        self.table_textview.get_buffer().set_text(self.table.get_create_table())
        if self.table_properties:
            self.table_properties.update()
        if self.table_fields:
            self.table_fields.refresh()
        if self.table.is_table:
            if self.table_indexes:
                self.table_indexes.refresh()

    def table_changed(self, table):
        """
        @param table: MySqlTable
        """
        self.table_textview.get_buffer().set_text(self.table.get_create_table())
        self.tab_label.set_text('Table: %s' % table.name)
        # print 'Table `%s` fired CHANGED event!' % table.name

    def destroy(self):
        """
        Cleanup
        """
        self.data_view.destroy()
        del self.data_view
        del self.emma
        del self.notebook
        del self.status_text
        del self.table
        del self.table_data_result
        del self.table_fields
        del self.table_indexes
        del self.table_properties
        del self.table_textview
        del self.toolbar
        super(TabTable, self).destroy()
        gc.collect()
