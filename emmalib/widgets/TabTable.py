# coding=utf8

import gtk
import gobject
from BaseTab import BaseTab
from ResultCellRenders import *


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
        )
        self.tv_fields = gtk.TreeView()
        self.tv_fields.set_rules_hint(True)
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
        self.tv_indexes.set_rules_hint(True)
        self.tv_indexes.set_model(self.tv_indexes_model)
        sw_indexes.add(self.tv_indexes)

        # init Table properties
        self.table_properties = gtk.Table()

        # init Create script view
        sql_create_tab = gtk.ScrolledWindow()
        self.table_textview = gtk.TextView()
        sql_create_tab.add(self.table_textview)

        # Data
        sw_data = gtk.ScrolledWindow()
        sw_data.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.tv_data_model = None
        self.tv_data = gtk.TreeView()
        self.tv_data.set_rules_hint(True)
        self.tv_data.set_model(self.tv_indexes_model)
        sw_data.add(self.tv_data)
        self.data_loaded = False

        self.ui.append_page(sw_fields, gtk.Label('Fields'))
        self.ui.append_page(sw_indexes, gtk.Label('Indexes'))
        self.ui.append_page(sw_data, gtk.Label('Data'))
        self.ui.append_page(self.table_properties, gtk.Label('Properties'))
        self.ui.append_page(sql_create_tab, gtk.Label('SQL: Create'))

        self.update()

        self.ui.connect('switch-page', self.on_notebook_switch_page)

        self.ui.show_all()

    def on_notebook_switch_page(self, nb, pointer, page_num):
        if page_num == 2 and not self.data_loaded:
            self.load_data()

    def load_data(self):
        result = self.table.db.host.query_dict('SELECT * FROM %s' % self.table.name, append_to_log=False, encoding='utf8')
        if not result:
            return
        #
        #   Build list store with sort and data columns
        #   Make map of result column index, its display column and sort column
        #
        columns = []
        sort_display_map = []
        i = 0
        ci = 0
        for t in result['types']:
            columns.append(t)
            sort_index = i
            disp_index = sort_index
            i += 1
            if t == gobject.TYPE_LONG or t == gobject.TYPE_INT or t == gobject.TYPE_FLOAT:
                columns.append(gobject.TYPE_STRING)
                disp_index = i
                i += 1
            sort_display_map.append((ci, sort_index, disp_index))
            ci += 1
        #
        #   Add it all to model and in treeview
        #
        self.tv_data_model = gtk.ListStore(*columns)
        self.tv_data.set_model(self.tv_data_model)
        #
        #   Add treeview columns according to previously built index/sort/data map
        #
        for column_index, sort_index, disp_index in sort_display_map:
            title = result['cols'][column_index].replace("_", "__").replace("[\r\n\t ]+", " ")
            self.column_insert(title, sort_index, disp_index)

        #
        #   Fill in List store with data
        #   In case of long and int columns - two columns added
        #   to make sorting and rendering properly
        #
        for row in result['rows']:
            model_row = []
            for col in result['cols']:
                ci = result['cols'].index(col)
                if result['types'][ci] == gobject.TYPE_LONG:
                    if row[col] is None:
                        v = 0
                    else:
                        v = long(row[col])
                    model_row.append(v)
                    model_row.append(row[col])
                elif result['types'][ci] == gobject.TYPE_INT:
                    if row[col] is None:
                        v = 0
                    else:
                        v = int(row[col])
                    model_row.append(v)
                    model_row.append(row[col])
                elif result['types'][ci] == gobject.TYPE_FLOAT:
                    if row[col] is None:
                        v = 0
                    else:
                        v = float(row[col])
                    model_row.append(v)
                    model_row.append(row[col])
                elif result['types'][ci] == gobject.TYPE_STRING:
                    if row[col] is None:
                        #
                        #   Add as none
                        #
                        model_row.append(None)
                    else:
                        try:
                            #
                            #   Add as ascii
                            #
                            row[col].decode('ascii')
                            v = str(row[col])
                        except:
                            try:
                                #
                                #   Add as converted utf8
                                #
                                v = row[col].decode('utf-8')
                            except UnicodeError:
                                #
                                #   Can't convert to string
                                #   Then it might be a binary
                                #
                                v = '<BINARY>'
                        model_row.append(v)
            try:
                self.tv_data_model.append(model_row)
            except:
                pass

    def column_insert(self, title, sort_column_index, display_column_index):
        text_renderer = gtk.CellRendererText()
        ci = self.tv_data.insert_column_with_data_func(
            -1,
            title,
            text_renderer,
            render_mysql_string,
            display_column_index)
        col = self.tv_data.get_column(ci-1)
        col.set_sort_column_id(sort_column_index)

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
        self.tv_fields.append_column(gtk.TreeViewColumn("Name", gtk.CellRendererText(), text=0))
        self.tv_fields.append_column(gtk.TreeViewColumn("Type", gtk.CellRendererText(), text=1))
        self.tv_fields.append_column(gtk.TreeViewColumn("Null", gtk.CellRendererText(), text=2))
        self.tv_fields.append_column(gtk.TreeViewColumn("Default", gtk.CellRendererText(), text=3))
        for f in self.table.fields:
            self.tv_fields_model.append(
                (
                    f.name,
                    f.type,
                    f.is_null,
                    f.default,
                )
            )

    def build_indexes(self):
        self.tv_indexes.append_column(gtk.TreeViewColumn("Name", gtk.CellRendererText(), text=0))
        self.tv_indexes.append_column(gtk.TreeViewColumn("Column", gtk.CellRendererText(), text=1))
        self.tv_indexes.append_column(gtk.TreeViewColumn("Unique", gtk.CellRendererText(), text=2))
        for ix in self.table.indexes:
            self.tv_indexes_model.append(
                (
                    ix.name,
                    ix.column,
                    ix.is_unique,
                )
            )

    def cleanup_tv_data(self):
        for col in self.tv_data.get_columns():
            self.tv_data.remove_column(col)
        if self.tv_data_model:
            self.tv_data_model.clear()
