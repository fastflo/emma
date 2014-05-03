import gtk


class TabTable(gtk.HPaned):
    def __init__(self, emma):
        super(TabTable, self).__init__()

        self.emma = emma

        self.table_description_size = (0, 0)
        self.table_property_labels = []
        self.table_property_entries = []

        # init left
        sw_left = gtk.ScrolledWindow()
        viewport = gtk.Viewport()
        self.left_vbox = gtk.VBox()
        self.table_properties = gtk.Table()
        self.table_description = gtk.Table()
        self.left_vbox.pack_start(self.table_properties)
        self.left_vbox.pack_start(gtk.HSeparator())
        self.left_vbox.pack_end(self.table_description)
        viewport.add(self.left_vbox)
        sw_left.add(viewport)

        # init right
        sw_right = gtk.ScrolledWindow()
        self.table_textview = gtk.TextView()
        sw_right.add(self.table_textview)

        self.add1(sw_left)
        self.add2(sw_right)

        self.set_position(300)

        self.show_all()

    def update(self, path=None):
        if not path:
            path, column = self.emma.connections_tv.get_cursor()
            if len(path) != 3:
                return
        _iter = self.emma.connections_tv.connections_model.get_iter(path)
        th = self.emma.connections_tv.connections_model.get_value(_iter, 0)

        table = self.table_properties
        prop_count = len(th.props)
        if len(self.table_property_labels) != prop_count:
            for c in self.table_property_labels:
                table.remove(c)
            for c in self.table_property_entries:
                table.remove(c)
            self.table_property_labels = []
            self.table_property_entries = []
            table.resize(prop_count, 2)
            r = 0
            for h, p in zip(th.db.status_headers, th.props):
                l = gtk.Label(h)
                l.set_alignment(0, 0.5)
                e = gtk.Entry()
                e.set_editable(False)
                if p is None:
                    p = ""
                e.set_text(p)
                table.attach(l, 0, 1, r, r + 1, gtk.FILL, 0)
                table.attach(e, 1, 2, r, r + 1, gtk.EXPAND | gtk.FILL | gtk.SHRINK, 0)
                l.show()
                e.show()
                self.table_property_labels.append(l)
                self.table_property_entries.append(e)
                r += 1
        else:
            r = 0
            for h, p in zip(th.db.status_headers, th.props):
                l = self.table_property_labels[r]
                e = self.table_property_entries[r]
                l.set_label(h)
                if p is None:
                    p = ""
                e.set_text(p)
                r += 1

        tv = self.table_textview
        tv.get_buffer().set_text(th.get_create_table())

        t = self.table_description
        for c in t.get_children():
            self.table_description.remove(c)
        self.table_description.resize(len(th.describe_headers), len(th.fields) + 1)
        c = 0
        for h in th.describe_headers:
            l = gtk.Label(h)
            t.attach(l, c, c + 1, 0, 1, gtk.FILL, 0)
            l.show()
            c += 1
        r = 1
        for fn in th.field_order:
            v = th.fields[fn]
            for c in range(len(th.describe_headers)):
                s = v[c]
                if s is None:
                    s = ""
                l = gtk.Label(s)
                t.attach(l, c, c + 1, r, r + 1, gtk.FILL, 0)
                l.set_alignment(0, 0.5)
                l.set_selectable(True)
                l.show()
            r += 1
        self.left_vbox.check_resize()
