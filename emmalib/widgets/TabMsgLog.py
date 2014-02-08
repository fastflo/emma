import gtk
import time
import gobject


class TabMsgLog(gtk.ScrolledWindow):
    def __init__(self,emma):
        super(TabMsgLog, self).__init__()
        self.emma = emma
        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.tv = gtk.TreeView()
        self.tv.set_model(self.model)
        self.tv.append_column(gtk.TreeViewColumn("Time", gtk.CellRendererText(), text=0))
        self.tv.append_column(gtk.TreeViewColumn("Message", gtk.CellRendererText(), text=1))

        self.tv.connect('button-press-event', self.on_msg_tv_button_press_event)

        self.add(self.tv)
        self.show_all()

    def log(self, log):
        if not log:
            return
        log.replace(
            "You have an error in your SQL syntax.  Check the manual that corresponds to your MySQL server version for the right syntax to use near",
            "syntax error at "
        )
        now = time.time()
        now = int((now - int(now)) * 100)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        if now:
            timestamp = "%s.%02d" % (timestamp, now)
        _iter = self.model.append((timestamp, log))
        self.tv.scroll_to_cell(self.model.get_path(_iter))
        self.emma.message_notebook.set_current_page(self.emma.message_notebook.page_num(self))

    def on_msg_tv_button_press_event(self, tv, event):
        if not event.button == 3:
            return False
        res = tv.get_path_at_pos(int(event.x), int(event.y))
        self.emma.xml.get_widget("messages_popup").popup(None, None, None, event.button, event.time)
        return True

    def on_messages_popup(self, item):
        if item.name == "clear_messages":
            self.model.clear()

