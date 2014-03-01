import gtk


class TabBlobView(gtk.VBox):
    def __init__(self, emma):
        super(TabBlobView, self).__init__()

        self.emma = emma

        hbox = gtk.HBox()
        hbox.set_spacing(5)

        self.blob_wrap_check = gtk.CheckButton('Wrap Text')
        hbox.pack_start(self.blob_wrap_check, False, True)

        self.blob_update = gtk.Button('Update', gtk.STOCK_REFRESH)
        hbox.pack_start(self.blob_update, False, True)

        hbox.pack_start(gtk.VSeparator(), False, True)

        self.blob_save = gtk.Button('Save', gtk.STOCK_SAVE)
        hbox.pack_start(self.blob_save, False, True)

        self.blob_load = gtk.Button('Load', gtk.STOCK_OPEN)
        hbox.pack_start(self.blob_load, False, True)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.tv = gtk.TextView()
        self.tv.set_editable(False)
        sw.add(self.tv)

        self.pack_start(hbox, False, True)
        self.pack_end(sw, True, True)

        self.show_all()

