# coding=utf8

import gtk
import gobject
from BaseTab import BaseTab
from ResultView import ResultView


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

        #
        #   PROPERTIES
        #
        self.table_properties = table.get_table_properties_widget()
        if self.table_properties:
            self.ui.append_page(self.table_properties, gtk.Label('Properties'))

        #
        #   FIELDS
        #
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
        self.ui.append_page(sw_fields, gtk.Label('Fields'))

        #
        #   INDEXES
        #
        if self.table.is_table:
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
            self.ui.append_page(sw_indexes, gtk.Label('Indexes'))

        #
        #   DATA
        #
        self.results_view = ResultView()
        self.results_view.enable_sorting = True
        self.ui.append_page(self.results_view, gtk.Label('Data'))

        #
        #   CREATE TABLE/VIEW SQL
        #
        sql_create_tab = gtk.ScrolledWindow()
        self.table_textview = gtk.TextView()
        sql_create_tab.add(self.table_textview)
        self.ui.append_page(sql_create_tab, gtk.Label('SQL: Create'))

        self.update()

        self.ui.connect('switch-page', self.on_notebook_switch_page)

        self.ui.show_all()
        self.ui.set_current_page(0)

    def on_notebook_switch_page(self, nb, pointer, page_num):
        text = self.ui.get_tab_label_text(self.ui.get_nth_page(page_num))
        if text == 'Data' and not self.results_view.data_loaded:
            self.results_view.load_data(self.table.get_all_records())

    def update(self):
        self.table_textview.get_buffer().set_text(self.table.get_create_table())
        if self.table_properties:
            self.table_properties.update()
        self.build_fields()
        if self.table.is_table:
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
        if self.table.is_view:
            return

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

