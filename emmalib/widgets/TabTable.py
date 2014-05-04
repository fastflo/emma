import gtk
import gobject
from BaseTab import BaseTab


class TabTable(BaseTab):
    def __init__(self, emma, table):
        """
        @param emma: Emma
        """
        super(TabTable, self).__init__()

        self.ui = gtk.Notebook()
        self.tab_label.set_text('Table: %s' % table.name)

        self.emma = emma
        self.table = table

        self.table_description_size = (0, 0)
        self.table_property_labels = []
        self.table_property_entries = []

        # fields
        sw_fields = gtk.ScrolledWindow()
        sw_fields.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.tv_fields_model = gtk.ListStore(
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
        )
        self.tv_fields = gtk.TreeView()
        self.tv_fields.set_model(self.tv_fields_model)
        sw_fields.add(self.tv_fields)

        # Indexes
        sw_indexes = gtk.ScrolledWindow()
        sw_indexes.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.tv_indexes_model = gtk.ListStore(
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
        )
        self.tv_indexes = gtk.TreeView()
        self.tv_indexes.set_model(self.tv_indexes_model)
        sw_indexes.add(self.tv_indexes)

        # init Table properties
        self.table_properties = gtk.Table()

        # init Create script view
        sql_create_tab = gtk.ScrolledWindow()
        self.table_textview = gtk.TextView()
        sql_create_tab.add(self.table_textview)

        self.ui.append_page(sw_fields, gtk.Label('Fields'))
        self.ui.append_page(sw_indexes, gtk.Label('Indexes'))
        self.ui.append_page(self.table_properties, gtk.Label('Properties'))
        self.ui.append_page(sql_create_tab, gtk.Label('SQL: Create'))

        self.update()

        self.ui.show_all()

    def update(self):
        th = self.table

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

        self.table_textview.get_buffer().set_text(th.get_create_table())
        self.build_fields()
        self.build_indexes()

    def build_fields(self):
        ix = 0
        for h in self.table.describe_headers:
            self.tv_fields.append_column(gtk.TreeViewColumn(h, gtk.CellRendererText(), text=ix))
            ix += 1
        for fn in self.table.field_order:
            v = self.table.fields[fn]
            self.tv_fields_model.append(v)

    def build_indexes(self):
        self.tv_indexes.append_column(gtk.TreeViewColumn("Name", gtk.CellRendererText(), text=0))
        self.tv_indexes.append_column(gtk.TreeViewColumn("Column", gtk.CellRendererText(), text=1))
        self.tv_indexes.append_column(gtk.TreeViewColumn("Unique", gtk.CellRendererText(), text=2))
        for ix in self.table.indexes:
            print ix
            self.tv_indexes_model.append(
                (
                    ix.name,
                    ix.column,
                    ix.is_unique,
                )
            )
