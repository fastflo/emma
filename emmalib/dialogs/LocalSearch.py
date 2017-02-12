"""
Emma's Local Search dialog
"""
import os
import sys
import re

import gtk

from emmalib import dialogs
from emmalib import glade_path


class LocalSearch(object):
    """
    Local Search Dialog
    """
    def __init__(self):
        self.window = None
        self.entry = None
        self.start_at_first_row = None
        self.case_sensitive = None

        glade_file = os.path.join(glade_path, 'dialogs', "LocalSearch.glade")
        if not os.access(glade_file, os.R_OK):
            # print glade_file, "not found!"
            sys.exit(-1)

        # print "glade file: %r" % glade_file
        self.xml = gtk.glade.XML(glade_file)
        self.xml.signal_autoconnect(self)

        # Local Search Window
        self.window = self.xml.get_widget("localsearch_window")
        self.entry = self.xml.get_widget("local_search_entry")
        self.entry.connect(
            "activate",
            lambda *a: self.window.response(gtk.RESPONSE_OK)
        )
        self.start_at_first_row = self.xml.get_widget("search_start_at_first_row")
        self.case_sensitive = self.xml.get_widget("search_case_sensitive")

    def run(self, query=None, again=False):
        """
        :param query:
        :param again:
        :return:
        """
        self.start_at_first_row.set_active(False)
        if not again or not self.entry.get_text():
            self.entry.grab_focus()
            answer = self.window.run()
            self.window.hide()
            if not answer == gtk.RESPONSE_OK:
                return
        regex = self.entry.get_text()
        if self.case_sensitive.get_active():
            regex = "(?i)" + regex
        query_model = query.model
        fields = query_model.get_n_columns()
        _start = query_model.get_iter_root()
        start_column_index = -1
        start_path = None
        if not self.start_at_first_row.get_active():
            start_path, start_column = query.treeview.get_cursor()
            if start_path:
                _start = query_model.get_iter(start_path)
                for k in range(fields):
                    if query.treeview.get_column(k) == start_column:
                        start_column_index = k
                        break
            else:
                start_path = None
        while _start:
            for k in range(fields):
                query_model_value = query_model.get_value(_start, k)
                if query_model_value is None:
                    continue
                if re.search(regex, query_model_value):
                    path = query_model.get_path(_start)
                    if start_path and start_path == path and k <= start_column_index:
                        continue  # skip!
                    column = query.treeview.get_column(k)
                    query.treeview.set_cursor(path, column)
                    query.treeview.scroll_to_cell(path, column)
                    query.treeview.grab_focus()
                    return
            _start = query_model.iter_next(_start)
        dialogs.show_message(
            "local regex search",
            "sorry, no match found!\ntry to search from the beginning "
            "or execute a less restrictive query...")
