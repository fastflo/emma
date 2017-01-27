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

import os
import gtk
import sys

import dialogs


class SaveResultCsv(gtk.ToolButton):

    def __init__(self, query, emma):
        """
        @param query: QueryTab
        @param emma: Emma
        """
        self.emma = emma
        self.query = query
        super(SaveResultCsv, self).__init__()

        self.set_label('Save as CSV')
        self.set_icon_name(gtk.STOCK_SAVE_AS)
        self.set_tooltip_text('Save result as CSV file')

        self.connect('clicked', self.on_save_result_clicked)
        self.set_sensitive(False)

    def on_save_result_clicked(self, button):
        d = self.emma.assign_once(
            "save results dialog",
            gtk.FileChooserDialog, "save results", self.emma.mainwindow, gtk.FILE_CHOOSER_ACTION_SAVE,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))

        d.set_default_response(gtk.RESPONSE_ACCEPT)
        answer = d.run()
        d.hide()
        if not answer == gtk.RESPONSE_ACCEPT:
            return
        filename = d.get_filename()
        if os.path.exists(filename):
            if not os.path.isfile(filename):
                dialogs.show_message("save results", "%s already exists and is not a file!" % filename)
                return
            if not dialogs.confirm(
                    "overwrite file?",
                    "%s already exists! do you want to overwrite it?" % filename, self.emma.mainwindow):
                return
        q = self.query
        _iter = q.model.get_iter_first()
        indices = range(q.model.get_n_columns())
        field_delim = self.emma.config.get("save_result_as_csv_delim")
        line_delim = self.emma.config.get("save_result_as_csv_line_delim")
        try:
            fp = file(filename, "wb")
            for search, replace in {"\\n": "\n", "\\r": "\r", "\\t": "\t", "\\0": "\0"}.iteritems():
                field_delim = field_delim.replace(search, replace)
                line_delim = line_delim.replace(search, replace)
            while _iter:
                row = q.model.get(_iter, *indices)
                for field in row:
                    value = field
                    if value is None:
                        value = ""
                    fp.write(value.replace(field_delim, "\\" + field_delim))
                    fp.write(field_delim)
                fp.write(line_delim)
                _iter = q.model.iter_next(_iter)
            fp.close()
        except:
            dialogs.show_message("save results", "error writing query to file %s: %s" % (filename, sys.exc_value))
