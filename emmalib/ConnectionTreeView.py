import os
import gtk
import gtk.glade
import time
import gobject
import dialogs
import widgets
from Config import Config
from ConnectionWindow import ConnectionWindow


class ConnectionsTreeView(gtk.TreeView):
    def __init__(self, emma=None):

        self.emma = emma

        self.current_host = None

        self.icons = {}
        self.load_icons()

        self.connections_model = gtk.TreeStore(gobject.TYPE_PYOBJECT)
        super(ConnectionsTreeView, self).__init__(self.connections_model)
        #self.set_model(self.connections_model)

        col = gtk.TreeViewColumn("Hosts")

        pixbuf_renderer = gtk.CellRendererPixbuf()
        col.pack_start(pixbuf_renderer, False)
        col.set_cell_data_func(pixbuf_renderer, self.render_connections_pixbuf)

        text_renderer = gtk.CellRendererText()
        col.pack_end(text_renderer)
        col.set_cell_data_func(text_renderer, self.render_connections_text)

        self.append_column(col)
        self.connect("row-expanded", self.on_row_expanded)
        self.connect("row-collapsed", self.on_row_collapsed)
        self.connect("row-activated", self.on_connections_row_activated)
        self.connect("button-release-event", self.on_connections_button_release)
        self.connect("cursor-changed", self.on_connections_tv_cursor_changed)

        self.pop_up_host = widgets.PopUpHost()
        self.pop_up_host.connect('item-selected', self.on_host_popup)

        self.connection_window = ConnectionWindow(self)

        self.load_from_config()

    def load_from_config(self):
        keys = self.emma.config.config.keys()
        for name in keys:
            value = self.emma.config.config[name]
            if not self.emma.config.unpickled:
                prefix = "connection_"
                if name.startswith(prefix) and value == "::sqlite::":
                    print 'sqlite'
                    filename = name[len(prefix):]
                    self.add_sqlite(filename)
                    continue
                if name.startswith(prefix):
                    print 'mysql'
                    v = value.split(",")
                    port = ""
                    p = v[0].rsplit(":", 1)
                    if len(p) == 2:
                        port = p[1]
                        v[0] = p[0]
                    self.add_mysql_host(name[len(prefix):], v[0], port, v[1], v[2], v[3])
                    pass

    def on_connections_row_activated(self, tv, path, col):
        depth = len(path)
        self.emma.add_msg_log('on_connections_row_activated level %s' % depth)
        _iter = self.connections_model.get_iter(path)
        o = self.connections_model.get_value(_iter, 0)

        try:
            nb = self.emma.xml.get_widget("main_notebook")
        except:
            nb = None
        if depth == 1:
            self.current_host = host = o
            if host.connected:
                self.current_host = None
                host.close()
            else:
                host.connect()
                if not host.connected:
                    return
                self.emma.refresh_processlist()
                if nb:
                    nb.set_current_page(1)
            self.redraw_host(host, _iter, True)
            if self.emma.current_query:
                self.emma.current_query.set_current_host(self.current_host)

        elif depth == 2:
            self.current_host = o.host
            new_tables = o.refresh()
            self.redraw_db(o, _iter, new_tables, True)
            self.emma.redraw_tables()
            o.host.select_database(o)
            if self.emma.current_query:
                self.emma.current_query.set_current_db(o)

        elif depth == 3:
            self.current_host = host = o.db.host
            host.select_database(o.db)
            table = o
            if self.emma.current_query:
                self.emma.current_query.set_current_db(table.db)
            ait = self.emma.config.get("autorefresh_interval_table")
            if not table.fields or (time.time() - table.last_field_read) > ait:
                table.refresh()
                self.redraw_table(o, _iter)

            try:
                if self.emma.first_template:
                    nb.set_current_page(4)
                    self.emma.on_template(None, self.emma.first_template)
                elif nb.get_current_page() < 3:
                    nb.set_current_page(3)
            except AttributeError:
                print 'Debug mode: no access to full emma object'

        else:
            print "No Handler for tree-depth", depth
        return

    def on_row_expanded(self, tv, _iter, path):
        o = tv.get_model().get_value(_iter, 0)
        if len(path) > 3:
            return
        o.expanded = True

    def on_row_collapsed(self, tv, _iter, path):
        o = tv.get_model().get_value(_iter, 0)
        if len(path) > 3:
            return
        o.expanded = False

    def on_connections_tv_cursor_changed(self, tv):
        path, column = tv.get_cursor()
        nb = self.emma.xml.get_widget("main_notebook")
        if path is None:
            print "get_cursor() returned none. don't know which datebase is selected."
            return

        if len(path) == 3 and nb.get_current_page() == 3:
            print "update table view..."
            self.emma.update_table_view(path)

        if self.emma.current_query:
            q = self.emma.current_query
        else:
            return

        q.last_path = path
        if len(path) == 1:
            i = self.connections_model.get_iter(path)
            o = self.connections_model[i][0]
            q.set_current_host(o)
        elif len(path) >= 2:
            i = self.connections_model.get_iter(path[0:2])
            o = self.connections_model[i][0]
            q.set_current_db(o)

    def on_connections_button_release(self, tv, event):
        if not event.button == 3:
            return False
        res = tv.get_path_at_pos(int(event.x), int(event.y))
        menu = None
        if not res or len(res[0]) == 1:
            self.emma.xml.get_widget("modify_connection").set_sensitive(not not res)
            self.emma.xml.get_widget("delete_connection").set_sensitive(not not res)
            connected_host = False
            if res:
                model = self.connections_model
                _iter = model.get_iter(res[0])
                host = model.get_value(_iter, 0)
                connected_host = host.connected
            self.emma.xml.get_widget("new_database").set_sensitive(connected_host)
            self.emma.xml.get_widget("refresh_host").set_sensitive(connected_host)
            #menu = self.emma.xml.get_widget("connection_menu")
            self.pop_up_host.popup(None, None, None, event.button, event.time)
        elif len(res[0]) == 2:
            menu = self.emma.xml.get_widget("database_popup")
        elif len(res[0]) == 3:
            menu = self.emma.xml.get_widget("table_popup")

        if menu:
            menu.popup(None, None, None, event.button, event.time)

        return True

    def redraw_host(self, host, _iter, expand=False):
        print "redraw host", host.name
        if host.expanded:
            expand = True

        # first remove exiting children of that node
        i = self.connections_model.iter_children(_iter)
        while i and self.connections_model.iter_is_valid(i):
            self.connections_model.remove(i)

        # now add every database
        keys = host.databases.keys()
        keys.sort()
        for name in keys:
            db = host.databases[name]
            i = self.connections_model.append(_iter, (db,))
            if expand:
                self.expand_row(self.connections_model.get_path(_iter), False)
                expand = False
            self.redraw_db(db, i)

    def redraw_db(self, db, _iter, new_tables=None, force_expand=False):
        #print "redraw db", db.name
        if not _iter:
            print "Error: invalid db-iterator:", _iter
            return
        path = self.connections_model.get_path(_iter)
        if db.expanded:
            force_expand = True
        i = self.connections_model.iter_children(_iter)
        while i and self.connections_model.iter_is_valid(i):
            self.connections_model.remove(i)
        keys = db.tables.keys()
        keys.sort()
        iterators = {}
        for name in keys:
            table = db.tables[name]
            i = self.connections_model.append(_iter, (table,))
            if force_expand:
                self.expand_row(path, False)
                force_expand = False
            self.redraw_table(table, i)
            iterators[name] = i
        if not new_tables:
            return
        for name in new_tables:
            table = db.tables[name]
            table.refresh(False)
            self.redraw_table(table, iterators[name])
            self.emma.process_events()

    def redraw_table(self, table, _iter):
        #print "redraw table", table.name
        if table.expanded:
            self.expand_row(self.connections_model.get_path(_iter), False)
        i = self.connections_model.iter_children(_iter)
        while i and self.connections_model.iter_is_valid(i):
            self.connections_model.remove(i)
        for field in table.field_order:
            i = self.connections_model.append(_iter, (table.fields[field],))

    def render_connections_pixbuf(self, column, cell, model, itr):
        d = model.iter_depth(itr)
        o = model.get_value(itr, 0)
        if isinstance(o, str):
            return
        if d == 0:
            if o.connected:
                cell.set_property("pixbuf", self.icons["host"])
            else:
                cell.set_property("pixbuf", self.icons["offline_host"])
        elif d == 1:
            cell.set_property("pixbuf", self.icons["db"])
        elif d == 2:
            cell.set_property("pixbuf", self.icons["table"])
        elif d == 3:
            cell.set_property("pixbuf", self.icons["field"])
        else:
            print "unknown depth %r for render_connections_pixbuf with object %r" % (d, o)

    def render_connections_text(self, column, cell, model, itr):
        d = model.iter_depth(itr)
        o = model.get_value(itr, 0)
        if isinstance(o, str):
            cell.set_property("text", o)
            return
        if d == 0:
            if o.connected:
                cell.set_property("text", o.name)
            else:
                cell.set_property("text", "(%s)" % o.name)
        elif d == 3:  # fields are only strings
            cell.set_property("text", "%s %s" % (o[0], o[1]))
        else:  # everything else has a name
            cell.set_property("text", o.name)
            #print "unknown depth", d," for render_connections_pixbuf with object", o

    def load_icons(self):
        from emmalib import icons_path
        for icon in ["offline_host", "host", "db", "table", "field"]:
            filename = os.path.join(icons_path, icon + ".png")
            try:
                self.icons[icon] = gtk.gdk.pixbuf_new_from_file(filename)
            except:
                print "could not load %r" % filename

    def add_mysql_host(self, name, hostname, port, user, password, database):
        from providers.mysql.MySqlHost import MySqlHost
        host = MySqlHost(self.emma.add_sql_log, self.emma.add_msg_log, name, hostname, port, user, password, database,
                         self.emma.config.get("connect_timeout"))
        _iter = self.connections_model.append(None, [host])
        host.set_update_ui(self.redraw_host, _iter)

    def add_sqlite(self, filename):
        from providers.sqlite.SQLiteHost import SQLiteHost
        host = SQLiteHost(self.emma.add_sql_log, self.emma.add_msg_log, filename)
        _iter = self.connections_model.append(None, [host])
        host.set_update_ui(self.redraw_host, _iter)

    def on_table_popup(self, item):
        path, column, _iter, table = self.get_current_table()
        what = item.name

        if what == "refresh_table":
            table.refresh()
            self.redraw_table(table, _iter)
            self.update_table_view()
        elif what == "truncate_table":
            if not dialogs.confirm("truncate table", "do you really want to truncate the <b>%s</b> table in database <b>%s</b> on <b>%s</b>?" % (table.name, table.db.name, table.db.host.name), self.mainwindow):
                return
            if table.db.query("truncate `%s`" % (table.name)):
                table.refresh()
                self.redraw_table(table, _iter)
                self.update_table_view()
        elif what == "drop_table":
            if not dialogs.confirm("drop table", "do you really want to DROP the <b>%s</b> table in database <b>%s</b> on <b>%s</b>?" % (table.name, table.db.name, table.db.host.name), self.mainwindow):
                return
            db = table.db
            if db.query("drop table `%s`" % (table.name)):
                new_tables = db.refresh()
                self.redraw_db(db, self.get_db_iter(db), new_tables)
                self.redraw_tables()
        elif what == "check_table":
            self.current_host = table.db.host
            self.current_host.select_database(table.db)
            self.xml.get_widget("main_notebook").set_current_page(4)
            self.on_execute_query_clicked(None, "check table `%s`" % table.name)
        elif what == "repair_table":
            self.current_host = table.db.host
            self.current_host.select_database(table.db)
            self.xml.get_widget("main_notebook").set_current_page(4)
            self.on_execute_query_clicked(None, "repair table `%s`" % table.name)

    def on_db_popup(self, item):
        self.emma.add_msg_log('on_db_popup')
        path, column = self.connections_tv.get_cursor()
        _iter = self.connections_model.get_iter(path)
        what = item.name
        db = self.connections_model.get_value(_iter, 0)

        if what == "refresh_database":
            new_tables = db.refresh()
            self.redraw_db(db, _iter, new_tables)
            self.redraw_tables()
        elif what == "drop_database":
            if not dialogs.confirm("drop database", "do you really want to drop the <b>%s</b> database on <b>%s</b>?" % (db.name, db.host.name), self.emma.mainwindow):
                return
            host = db.host
            if host.query("drop database`%s`" % (db.name)):
                host.refresh()
                self.redraw_host(host, self.get_host_iter(host))
        elif what == "new_table":
            name = dialogs.input_dialog("New table", "Please enter the name of the new table:", window=self.emma.mainwindow)
            if not name:
                return
            if db.query("create table `%s` (`%s_id` int primary key auto_increment)" % (name, name)):
                new_tables = db.refresh()
                self.redraw_db(db, self.get_db_iter(db), new_tables)
                self.redraw_tables()
        elif what == "check_tables":
            self.current_host = db.host
            self.current_host.select_database(db)
            self.xml.get_widget("main_notebook").set_current_page(4)
            self.on_execute_query_clicked(
                None,
                "check table %s" % (",".join(map(lambda s: "`%s`" % s, db.tables.keys()))))
        elif what == "repair_tables":
            self.current_host = db.host
            self.current_host.select_database(db)
            self.xml.get_widget("main_notebook").set_current_page(4)
            self.on_execute_query_clicked(
                None,
                "repair table %s" % (",".join(map(lambda s: "`%s`" % s, db.tables.keys()))))

    def on_host_popup(self, pop_up_host_object , item):
        self.emma.add_msg_log('on_db_popup')
        path, column = self.get_cursor()
        if path:
            _iter = self.connections_model.get_iter(path)
            host = self.connections_model.get_value(_iter, 0)
        else:
            _iter = None
            host = None
        what = item.name

        if what == "refresh_host":
            host.refresh()
            self.redraw_host(host, _iter)
        elif what == "new_database":
            name = dialogs.input_dialog("New database", "Please enter the name of the new database:",
                                        window=self.emma.mainwindow)
            if not name:
                return
            if host.query("Create database `%s`" % name):
                host.refresh()
                self.redraw_host(host, _iter)
        elif what == "modify_connection":
            self.connection_window.host = host
            self.connection_window.show("edit")
        elif what == "delete_connection":
            if not dialogs.confirm("Delete host", "Do you really want to drop the host <b>%s</b>?" % host.name,
                                   self.emma.mainwindow):
                return
            host.close()
            self.connections_model.remove(_iter)
            if self.current_host == host:
                self.current_host = None
            del self.emma.config.config["connection_%s" % host.name]
            host = None
            self.emma.config.save()
        elif what == "new_connection":
            self.connection_window.show("new")
        # elif what == "new_sqlite_connection":
        #     resp = self.sqlite_connection_dialog.run()
        #     self.sqlite_connection_dialog.hide()
        #     print "resp:", resp
        #     if resp:
        #         self.add_sqlite(self.sqlite_connection_dialog.get_filename())
        #         self.config.save()


if __name__ == '__main__':

    print __name__

    # class EmmaStub():
    #     def __init__(self):
    #         self.config = Config()
    #         self.config.load()
    #         self.current_query = False
    #         self.xml = gtk.glade.XML("/home/nick/Projects/emma/emmalib/emma.glade")
    #
    #     def add_msg_log(self, log):
    #         print log
    #
    #     def add_sql_log(self, log):
    #         print log
    #
    #     def refresh_processlist(self):
    #         pass
    #
    #     def process_events(self):
    #         pass
    #
    #     def redraw_tables(self):
    #         pass
    #
    # emmastub = EmmaStub()
    #
    # con = ConnectionsTreeView(emmastub)

    from emmalib import Emma

    con = ConnectionsTreeView(Emma())

    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.connect("delete_event", lambda *x: gtk.main_quit())
    window.set_size_request(640, 480)
    window.set_position(gtk.WIN_POS_CENTER)
    window.add(con)
    window.show_all()
    gtk.main()