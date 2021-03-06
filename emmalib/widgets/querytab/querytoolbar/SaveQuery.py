"""
Save Query
"""

import os
import sys
import gtk
from emmalib import dialogs


class SaveQuery(gtk.ToolButton):
    """
    @param query: QueryTab
    @param emma: Emma
    """

    def __init__(self, query, emma):
        super(SaveQuery, self).__init__()
        self.emma = emma
        self.query = query

        self.set_label('Save Query')
        self.set_icon_name(gtk.STOCK_SAVE)
        self.set_tooltip_text('Save Query To File (Ctrl+S)')

        self.connect('clicked', self.on_clicked)

    def on_clicked(self, _):
        """

        @param _:
        @return:
        """
        d = self.emma.assign_once(
            "save dialog",
            gtk.FileChooserDialog, "Save query", self.emma.mainwindow, gtk.FILE_CHOOSER_ACTION_SAVE,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))

        d.set_default_response(gtk.RESPONSE_ACCEPT)
        answer = d.run()
        d.hide()
        if not answer == gtk.RESPONSE_ACCEPT:
            return
        filename = d.get_filename()
        if os.path.exists(filename):
            if not os.path.isfile(filename):
                dialogs.show_message(
                    "save query",
                    "%s already exists and is not a file!" % filename
                )
                return
            if not dialogs.confirm(
                    "Overwrite file?",
                    "%s already exists! Do you want to overwrite it?" % filename,
                    self.emma.mainwindow
            ):
                return
        b = self.query.textview.get_buffer()
        query_text = b.get_text(b.get_start_iter(), b.get_end_iter())
        try:
            fp = file(filename, "wb")
            fp.write(query_text)
            fp.close()
        except:
            dialogs.show_message(
                "Save Query",
                "Error writing query to file %s: %s" % (filename, sys.exc_value)
            )
