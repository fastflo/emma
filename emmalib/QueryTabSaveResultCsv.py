import os
import gtk
import sys

import dialogs


class QueryTabSaveResultCsv:

    def __init__(self, query, emma):
        self.emma = emma
        self.query = query
        button = self.query.xml.get_widget('save_result')
        button.connect('clicked', self.on_save_result_clicked)

    def on_save_result_clicked(self, button):
        if not self.emma.current_query:
            return

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
        q = self.emma.current_query
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
