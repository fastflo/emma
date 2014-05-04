import gtk
import time
import gobject

from PopUpTabSqlLog import PopUpTabSqlLog


class TabSqlLog(gtk.ScrolledWindow):
    def __init__(self, emma):
        """
        @param emma: Emma
        """
        super(TabSqlLog, self).__init__()
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.emma = emma
        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.tv = gtk.TreeView()
        self.tv.set_model(self.model)
        self.tv.append_column(gtk.TreeViewColumn("Time", gtk.CellRendererText(), text=0))
        self.tv.append_column(gtk.TreeViewColumn("Query", gtk.CellRendererText(), markup=1))

        self.tv.connect('row-activated', self.on_sql_log_activate)
        self.tv.connect('button-press-event', self.on_sql_log_button_press)

        self.menu = PopUpTabSqlLog()
        self.menu.connect('item-selected', self.menu_item_selected)

        self.add(self.tv)
        self.show_all()

    def log(self, log):
        olog = log
        max_len = int(self.emma.config.get("query_log_max_entry_length"))
        if len(log) > max_len:
            log = log[0:max_len] + "\n/* query with length of %d bytes truncated. */" % len(log)

        if not log:
            return

        now = time.time()
        now = int((now - int(now)) * 100)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        if now:
            timestamp = "%s.%02d" % (timestamp, now)
        log = log.replace("<", "&lt;")
        log = log.replace(">", "&gt;")
        _iter = self.model.append((timestamp, log, olog))
        self.tv.scroll_to_cell(self.model.get_path(_iter))
        self.emma.message_notebook.set_current_page(self.emma.message_notebook.page_num(self))
        self.emma.process_events()

    def on_sql_log_activate(self, *args):
        tv, path, tvc = args
        query = tv.get_model()[path][2]
        self.emma.current_query.textview.get_buffer().set_text(query)
        return True

    def on_sql_log_button_press(self, tv, event):
        if not event.button == 3:
            return False
        res = tv.get_path_at_pos(int(event.x), int(event.y))
        if not res:
            return False
        tv.set_cursor_on_cell(res[0])
        self.menu.popup(None, None, None, event.button, event.time)
        return True

    def menu_item_selected(self, menu, item):
        if item.name == "clear_all_entries":
            self.model.clear()
            return True

        path, column = self.tv.get_cursor()

        if not path:
            return False
        row = self.model[path]
        if item.name == "copy_sql_log":
            self.emma.clipboard.set_text(row[2])
            self.emma.pri_clipboard.set_text(row[2])
        elif item.name == "set_as_query_text":
            self.emma.current_query.textview.get_buffer().set_text(row[2])
        if item.name == "delete_sql_log":
            _iter = self.model.get_iter(path)
            self.model.remove(_iter)
        return True
