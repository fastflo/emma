import gtk
import os
from stat import S_ISREG
import sys
from emmalib import dialogs


class LoadQuery(gtk.ToolButton):
    """
    @param query: QueryTab
    @param emma: Emma
    """
    def __init__(self, query, emma):
        super(LoadQuery, self).__init__()
        self.emma = emma
        self.query = query

        self.set_label('Load Query')
        self.set_icon_name(gtk.STOCK_OPEN)
        self.set_tooltip_text('Load Query From File (Ctrl+O)')

        self.connect('clicked', self.on_clicked)

    def on_clicked(self, _):
        """

        @param _:
        @return:
        """
        d = self.emma.assign_once(
            "load dialog",
            gtk.FileChooserDialog, "Load query", self.emma.mainwindow, gtk.FILE_CHOOSER_ACTION_OPEN,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))

        d.set_default_response(gtk.RESPONSE_ACCEPT)
        answer = d.run()
        d.hide()
        if not answer == gtk.RESPONSE_ACCEPT:
            return

        filename = d.get_filename()
        try:
            sbuf = os.stat(filename)
        except:
            dialogs.show_message("Load query", "%s does not exists!" % filename)
            return
        if not S_ISREG(sbuf.st_mode):
            dialogs.show_message("Load query", "%s exists, but is not a file!" % filename)
            return

        size = sbuf.st_size
        _max = int(self.emma.config.get("ask_execute_query_from_disk_min_size"))
        if size > _max:
            if dialogs.confirm("load query", """
<b>%s</b> is very big (<b>%.2fMB</b>)!
opening it in the normal query-view may need a very long time!
if you just want to execute this skript file without editing and
syntax-highlighting, i can open this file using the <b>execute file from disk</b> function.
<b>shall i do this?</b>""" % (filename, size / 1024.0 / 1000.0), self.emma.mainwindow):
                self.emma.on_execute_query_from_disk_activate(None, filename)
                return
        try:
            fp = file(filename, "rb")
            query_text = fp.read()
            fp.close()
        except:
            dialogs.show_message(
                "Load Query", "Error reading query from file %s: %s" % (filename, sys.exc_value))
            return
        self.query.textview.get_buffer().set_text(query_text)