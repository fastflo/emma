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

import re
import gtk

import dialogs


class QueryTabLocalSearch:

    def __init__(self, query, emma):
        """
        @param query: QueryTab
        @param emma: Emma
        """
        self.emma = emma
        self.query = query
        button = self.query.xml.get_widget('local_search_button')
        button.connect('clicked', self.on_local_search_button_clicked)

    def on_local_search_button_clicked(self, button, again=False):
        if not self.query.local_search.get_property("sensitive"):
            return

        query_view = self.query.treeview
        self.emma.local_search_start_at_first_row.set_active(False)
        if not again or not self.emma.local_search_entry.get_text():
            self.emma.local_search_entry.grab_focus()
            answer = self.emma.local_search_window.run()
            self.emma.local_search_window.hide()
            if not answer == gtk.RESPONSE_OK:
                return
        regex = self.emma.local_search_entry.get_text()
        if self.emma.local_search_case_sensitive.get_active():
            regex = "(?i)" + regex
        tm = self.query.model
        fields = tm.get_n_columns()
        _start = tm.get_iter_root()
        start_column_index = -1
        start_path = None
        if not self.emma.local_search_start_at_first_row.get_active():
            start_path, start_column = query_view.get_cursor()
            if start_path:
                _start = tm.get_iter(start_path)
                for k in range(fields):
                    if query_view.get_column(k) == start_column:
                        start_column_index = k
                        break
            else:
                start_path = None
        while _start:
            for k in range(fields):
                v = tm.get_value(_start, k)
                if v is None:
                    continue
                if re.search(regex, v):
                    path = tm.get_path(_start)
                    if start_path and start_path == path and k <= start_column_index:
                        continue  # skip!
                    column = query_view.get_column(k)
                    query_view.set_cursor(path, column)
                    query_view.scroll_to_cell(path, column)
                    query_view.grab_focus()
                    return
            _start = tm.iter_next(_start)
        dialogs.show_message(
            "local regex search",
            "sorry, no match found!\ntry to search from the beginning or execute a less restrictive query...")
