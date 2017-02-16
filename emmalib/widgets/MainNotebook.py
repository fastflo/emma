"""
MainNotebook
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
#
import gc
import gtk

from emmalib.widgets.TabProcessList import TabProcessList
from emmalib.widgets.TabTablesList import TabTablesList
from emmalib.widgets.QueryTab import QueryTab
from emmalib.widgets import TabTable


class MainNotebook(gtk.Notebook):
    """
    :param emma: Emma
    """

    def __init__(self, emma):
        super(MainNotebook, self).__init__()
        self.emma = emma
        self.queries = []
        self.query_count = 0
        self.tabs = []
        self.connect('switch-page', self.on_switch_page)
        self.set_scrollable(True)
        self.emma.events.on('on_table_dropped', self.on_table_dropped)

    def on_table_dropped(self, table):
        """
        :param table:
        """
        for tab in self.tabs:
            if isinstance(tab, TabTable):
                if tab.table == table:
                    self.close_generic_tab(None, tab)

    def on_switch_page(self, *args):
        """
        Set emma.current_query properly
        to keep backward compatibiluty for now
        :param args:
        """
        page_ui = self.get_nth_page(args[2])
        for q in self.queries:
            if q.ui == page_ui:
                if 'set_active' in dir(q):
                    q.set_active(True)
                self.emma.current_query = q
                q.database_event_box.on_click(None, None)
            else:
                if 'set_active' in dir(q):
                    q.set_active(False)

    def add_query_tab(self):
        """
        Add empty qury tab
        """
        q = QueryTab(self.emma)
        self.query_count += 1
        self.emma.current_query = q
        self.queries.append(q)
        new_page_index = self.append_page(q.get_ui(), q.get_label_ui())
        self.set_tab_reorderable(q.get_ui(), True)
        q.get_tab_close_button().connect('clicked', self.close_query_tab, q)
        self.set_current_page(new_page_index)
        q.textview.grab_focus()
        self.tabs.append(q)

    def close_query_tab(self, _, tab_class):
        """
        :param _: should be gtk button
        :param tab_class:
        :return:
        """
        if not tab_class:
            return False
        if len(self.queries) == 1:
            return False
        for q in self.queries:
            if q == tab_class:
                i = self.queries.index(q)
                del self.queries[i]
                i = self.tabs.index(q)
                del self.tabs[i]
                q.destroy()
                del q

                page_num = self.page_num(tab_class.get_ui())
                self.remove_page(page_num)
                gc.collect()
                return True
        return False

    def add_process_list_tab(self, host):
        """
        :param host:
        """
        # TODO: move to providers
        self.add_generic_tab(TabProcessList(self.emma, host))

    def add_tables_list_tab(self):
        """
        Adds "Tables List" tab
        """
        # TODO: move to providers
        self.add_generic_tab(TabTablesList(self.emma))

    def add_generic_tab(self, tab_class):
        """
        :param tab_class: type
        """
        ui = tab_class.get_ui()
        label = tab_class.get_label_ui()
        new_page_num = self.append_page(ui, label)
        self.set_tab_reorderable(ui, True)
        tab_class.get_tab_close_button().connect('clicked', self.close_generic_tab, tab_class)
        self.set_current_page(new_page_num)
        self.tabs.append(tab_class)

    def close_generic_tab(self, _, tab_class):
        """
        :param _:
        :param tab_class:
        :return:
        """
        if not tab_class:
            return
        page_num = self.page_num(tab_class.get_ui())
        self.remove_page(page_num)
        i = self.tabs.index(tab_class)
        del self.tabs[i]
        tab_class.destroy()
        del tab_class
        gc.collect()

    def close_current_tab(self):
        """
        :return:
        """
        page_num = self.get_current_page()
        if page_num < 0:
            return
        current_tab = self.get_nth_page(page_num)
        for tab in self.tabs:
            if tab.get_ui() == current_tab:
                if isinstance(tab, QueryTab):
                    self.close_query_tab(None, tab)
                else:
                    self.close_generic_tab(None, tab)
                gc.collect()
