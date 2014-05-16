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
        self.table_fields = table.get_table_fields_widget()
        if self.table_fields:
            self.ui.append_page(self.table_fields, gtk.Label('Fields'))

        #
        #   INDEXES
        #
        if self.table.is_table:
            self.table_indexes = table.get_table_indexes_widget()
            if self.table_indexes:
                self.ui.append_page(self.table_indexes, gtk.Label('Indexes'))

        #
        #   DATA
        #
        data_view_vbox = gtk.VBox()
        self.data_view_toolbar = gtk.Toolbar()
        self.data_view_toolbar.set_icon_size(gtk.ICON_SIZE_MENU)
        self.data_view_refresh = gtk.ToolButton(gtk.STOCK_REFRESH)
        self.data_view_refresh.set_is_important(True)
        self.data_view_refresh.connect('clicked', self.refresh_table_data)
        self.data_view_toolbar.add(self.data_view_refresh)
        self.data_view = ResultView()
        self.data_view.enable_sorting = True
        data_view_vbox.pack_start(self.data_view_toolbar, expand=False)
        data_view_vbox.pack_end(self.data_view)
        self.ui.append_page(data_view_vbox, gtk.Label('Data'))

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
        if text == 'Data' and not self.data_view.data_loaded:
            self.refresh_table_data()

    def refresh_table_data(self, *args):
        self.data_view.load_data(self.table.get_all_records())

    def update(self):
        self.table_textview.get_buffer().set_text(self.table.get_create_table())

        if self.table_properties:
            self.table_properties.update()

        if self.table_fields:
            self.table_fields.refresh()

        if self.table.is_table:
            if self.table_indexes:
                self.table_indexes.refresh()

