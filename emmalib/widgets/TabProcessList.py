import gtk
import gobject
from BaseTab import BaseTab

from PopUpProcessList import PopUpProcessList
from emmalib import dialogs

from ResultCellRenders import *


class TabProcessList(BaseTab):
    def __init__(self, emma, host):
        """
        @param emma: Emma
        """
        super(TabProcessList, self).__init__()

        self.ui = gtk.VBox(False, 0)
        self.tab_label.set_text('Process List')

        self.emma = emma
        self.host = host

        self.toolbar = gtk.Toolbar()
        self.toolbar.set_icon_size(gtk.ICON_SIZE_SMALL_TOOLBAR)
        self.button_refresh = gtk.ToolButton(gtk.STOCK_REFRESH)
        self.button_refresh.set_is_important(True)
        self.button_refresh.connect('clicked', self.refresh)
        self.toolbar.add(self.button_refresh)

        self.treeviewcontainer = gtk.ScrolledWindow()
        self.treeview = gtk.TreeView()
        self.treeview.set_rules_hint(True)
        self.treeview.connect('button-release-event', self.on_processlist_button_release)
        self.treeviewcontainer.add(self.treeview)

        self.ui.pack_start(self.toolbar, False, False)
        self.ui.pack_end(self.treeviewcontainer)

        self.model = None
        self.processlist_timer_running = False
        self.processlist_timer_interval = 0

        self.popup = PopUpProcessList()
        self.popup.connect('item-selected', self.on_kill_process)

        self.ui.show_all()

        self.refresh()

    def refresh(self, *args):
        if not self.host:
            return
        self.host.refresh_processlist()
        self.redraw()

    def redraw(self):
        if not self.host.processlist:
            return
        fields, rows = self.host.processlist
        if self.model:
            self.model.clear()

        for col in self.treeview.get_columns():
            self.treeview.remove_column(col)

        columns = [gobject.TYPE_STRING] * len(fields)
        self.model = gtk.ListStore(*columns)
        self.treeview.set_model(self.model)
        self.treeview.set_headers_clickable(True)
        _id = 0
        for field in fields:
            title = field[0].replace("_", "__")
            self.treeview.insert_column_with_data_func(
                -1, title, gtk.CellRendererText(),
                render_mysql_string, _id)
            _id += 1

        for proc in rows:
            self.model.append(proc)

        return

    def on_kill_process(self, *args):
        path, column = self.treeview.get_cursor()
        if not path or not self.host:
            return
        _iter = self.model.get_iter(path)
        process_id = self.model.get_value(_iter, 0)
        if not self.host.query("kill %s" % process_id):
            dialogs.show_message("sorry", "there was an error while trying to kill process_id %s!" % process_id)

    def on_processlist_button_release(self, tv, event):
        if not event.button == 3:
            return False
        res = tv.get_path_at_pos(int(event.x), int(event.y))
        if not res:
            return False
        self.popup.popup(None, None, None, event.button, event.time)

    def on_processlist_refresh_value_change(self, button):
        value = button.get_value()
        if self.processlist_timer_running:
            return
        self.processlist_timer_running = True
        self.processlist_timer_interval = value
        gobject.timeout_add(int(value * 1000), self.on_processlist_refresh_timeout, button)

    def on_processlist_refresh_timeout(self, button):
        value = button.get_value()
        if value < 0.1:
            self.processlist_timer_running = False
            return False
        self.refresh()
        if value != self.processlist_timer_interval:
            self.processlist_timer_running = False
            self.on_processlist_refresh_value_change(button)
            return False
        return True
