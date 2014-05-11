import os
import gtk
import sys

import dialogs


class TabBlobView(gtk.VBox):
    def __init__(self, emma):
        """
        @param emma: Emma
        """
        super(TabBlobView, self).__init__()

        self.emma = emma

        hbox = gtk.HBox()
        hbox.set_spacing(5)

        self.blob_wrap_check = gtk.CheckButton('Wrap Text')
        self.blob_wrap_check.connect('clicked', self.on_blob_wrap_check_clicked)
        hbox.pack_start(self.blob_wrap_check, False, True)

        self.blob_update = gtk.Button('Update', gtk.STOCK_REFRESH)
        self.blob_update.connect('clicked', self.on_blob_update_clicked)
        hbox.pack_start(self.blob_update, False, True)

        hbox.pack_start(gtk.VSeparator(), False, True)

        self.blob_save = gtk.Button('Save', gtk.STOCK_SAVE)
        self.blob_save.connect('clicked', self.on_blob_save_clicked)
        hbox.pack_start(self.blob_save, False, True)

        self.blob_load = gtk.Button('Load', gtk.STOCK_OPEN)
        self.blob_load.connect('clicked', self.on_blob_load_clicked)
        hbox.pack_start(self.blob_load, False, True)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.tv = gtk.TextView()
        self.tv.set_editable(False)
        self.tv.set_sensitive(False)
        sw.add(self.tv)

        self.pack_start(hbox, False, True)
        self.pack_end(sw, True, True)

        self.buffer = self.tv.get_buffer()
        self.visible = False
        self.encoding = None

        self.show_all()

    def on_blob_update_clicked(self, button):
        q = self.emma.current_query
        path, column = q.treeview.get_cursor()
        if not q.model:
            return

        b = self.tv.get_buffer()
        new_value = b.get_text(b.get_start_iter(), b.get_end_iter())

        col_max = q.model.get_n_columns()
        for col_num in range(col_max):
            if column == q.treeview.get_column(col_num):
                break
        else:
            return
        crs = column.get_cell_renderers()
        return q.on_query_change_data(crs[0],
                                      path, new_value, col_num,
                                      force_update=self.encoding != q.encoding)

    def on_blob_wrap_check_clicked(self, button):
        if button.get_active():
            self.tv.set_wrap_mode(gtk.WRAP_WORD)
        else:
            self.tv.set_wrap_mode(gtk.WRAP_NONE)

    def on_blob_load_clicked(self, button):
        d = self.emma.assign_once(
            "load dialog",
            gtk.FileChooserDialog,
            "load blob contents",
            self.emma.mainwindow,
            gtk.FILE_CHOOSER_ACTION_OPEN,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))

        d.set_default_response(gtk.RESPONSE_ACCEPT)
        answer = d.run()
        d.hide()
        if not answer == gtk.RESPONSE_ACCEPT:
            return

        filename = d.get_filename()
        try:
            fp = file(filename, "rb")
            query_text = fp.read().decode(self.emma.current_query.encoding, "ignore")
            fp.close()
        except:
            dialogs.show_message("load blob contents", "loading blob contents from file %s: %s" % (filename,
                                                                                                   sys.exc_value))
            return
        self.tv.get_buffer().set_text(query_text)

    def on_blob_save_clicked(self, button):
        d = self.emma.assign_once(
            "save dialog",
            gtk.FileChooserDialog,
            "save blob contents",
            self.emma.mainwindow,
            gtk.FILE_CHOOSER_ACTION_SAVE,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))

        d.set_default_response(gtk.RESPONSE_ACCEPT)
        answer = d.run()
        d.hide()
        if not answer == gtk.RESPONSE_ACCEPT:
            return
        filename = d.get_filename()
        if os.path.exists(filename):
            if not os.path.isfile(filename):
                dialogs.show_message("save blob contents", "%s already exists and is not a file!" % filename)
                return
            if not dialogs.confirm(
                    "overwrite file?", "%s already exists! do you want to overwrite it?" % filename,
                    self.emma.mainwindow):
                return
        b = self.tv.get_buffer()
        new_value = b.get_text(b.get_start_iter(), b.get_end_iter()).encode(self.emma.current_query.encoding, "ignore")
        try:
            fp = file(filename, "wb")
            fp.write(new_value)
            fp.close()
        except:
            dialogs.show_message("save blob contents", "error writing query to file %s: %s" % (filename, sys.exc_value))

