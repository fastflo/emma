import gobject
import gtk
from widgets import TabTable


class EventsManager(gobject.GObject):
    __gsignals__ = {
        'execute_query': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gtk.Object, str))
    }

    def __init__(self, emma):
        gobject.GObject.__init__(self)
        self.emma = emma

    def on_table_modified(self, table):
        new_tables = table.db.refresh()
        _iter = self.emma.connections_tv.get_db_iter(table.db)
        self.emma.connections_tv.redraw_db(table.db, _iter, new_tables)

    def on_table_dropped(self, table):
        self.on_table_modified(table)
        for tab in self.emma.main_notebook.tabs:
            if type(tab) == TabTable:
                if tab.table == table:
                    self.emma.main_notebook.close_generic_tab(None, tab)
