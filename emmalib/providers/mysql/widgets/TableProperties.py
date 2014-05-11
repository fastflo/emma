import gtk


class TableProperties(gtk.ScrolledWindow):

    def __init__(self, table):
        super(TableProperties, self).__init__()

        self.table = table

        self.table_description_size = (0, 0)
        self.table_property_labels = []
        self.table_property_entries = []

        vptp = gtk.Viewport()
        self.table_properties = gtk.Table()
        vptp.add(self.table_properties)
        self.add(vptp)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.show_all()

    def update(self):
        table = self.table_properties
        prop_count = len(self.table.props)
        if len(self.table_property_labels) != prop_count:
            for c in self.table_property_labels:
                table.remove(c)
            for c in self.table_property_entries:
                table.remove(c)
            self.table_property_labels = []
            self.table_property_entries = []
            table.resize(prop_count, 2)
            r = 0
            for h, p in zip(self.table.db.status_headers, self.table.props):
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
            for h, p in zip(self.table.db.status_headers, self.table.props):
                l = self.table_property_labels[r]
                e = self.table_property_entries[r]
                l.set_label(h)
                if p is None:
                    p = ""
                e.set_text(p)
                r += 1

