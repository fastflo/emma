import gobject
import gtk

from emmalib import emma_instance
from widgets import TabTable


class EventsManager:
    """
    Emma's global event manager
    """

    def __init__(self):
        self.__handlers__ = {}

    def on(self, event_name, event_callback):
        """
        :param event_name: str
        :param event_callback: function
        """
        if event_name not in self.__handlers__:
            self.__handlers__[event_name] = []
        self.__handlers__[event_name].append(event_callback)

    def trigger(self, event_name, *args):
        """
        :param event_name: str
        :param args: []
        """
        if event_name in self.__handlers__:
            for event in self.__handlers__[event_name]:
                if len(args) > 0:
                    event(args)
                else:
                    event()

    # TODO: rewrite to normal events
    @staticmethod
    def on_table_modified(table):
        """
        :param table:
        """
        new_tables = table.db.refresh()
        _iter = emma_instance.connections_tv.get_db_iter(table.db)
        emma_instance.connections_tv.redraw_db(table.db, _iter, new_tables)

    # TODO: rewrite to normal events
    @staticmethod
    def on_table_dropped(table):
        """
        :param table:
        """
        EventsManager.on_table_modified(table)
        for tab in emma_instance.main_notebook.tabs:
            if type(tab) == TabTable:
                if tab.table == table:
                    emma_instance.main_notebook.close_generic_tab(None, tab)
