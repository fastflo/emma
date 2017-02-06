"""
# -*- coding: utf-8 -*-
# emma
#
# Copyright (C) 2006 Florian Schmidt (flo@fastflo.de)
#               2014 Nickolay Karnaukhov (mr.electronick@gmail.com)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
"""
import gtk
import gobject
import dialogs
import widgets
import gtk.glade
from ConnectionWindow import ConnectionWindow
from Constants import *


class ConnectionsTreeView(gtk.TreeView):
    """
    @param emma: Emma
    """
    def __init__(self, emma=None):
        self.emma = emma

        self.current_host = None

        self.icons = {}
        self.load_icons()

        self.connections_model = gtk.TreeStore(gobject.TYPE_PYOBJECT)
        super(ConnectionsTreeView, self).__init__(self.connections_model)
        # self.set_model(self.connections_model)

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
        self.pop_up_database = widgets.PopUpDatabase()
        self.pop_up_database.connect('item-selected', self.on_db_popup)
        self.pop_up_table = widgets.PopUpTable()
        self.pop_up_table.connect('item-selected', self.on_table_popup)

        self.connection_window = ConnectionWindow(emma)

        self.emma.events.on('on_table_modified', self.on_table_modified)

        self.load_from_config()

    def on_table_modified(self, table):
        """
        :param table: MySqlTable
        """
        new_tables = table.db.refresh()
        _iter = self.get_db_iter(table.db)
        self.redraw_db(table.db, _iter, new_tables)

    def load_from_config(self):
        """
        Load config data
        """
        keys = self.emma.config.config.keys()
        for name in keys:
            value = self.emma.config.config[name]
            if not self.emma.config.unpickled:
                prefix = "connection_"
                if name.startswith(prefix) and value == "::sqlite::":
                    filename = name[len(prefix):]
                    self.add_sqlite(filename)
                    continue
                if name.startswith(prefix):
                    v = value.split(",")
                    port = ""
                    p = v[0].rsplit(":", 1)
                    if len(p) == 2:
                        port = p[1]
                        v[0] = p[0]
                    self.add_mysql_host(name[len(prefix):], v[0], port, v[1], v[2], v[3])
                    pass

    def on_connections_row_activated(self, tv, path, col):
        """
        :param tv: gtk.TreeView
        :param path: str
        :param col: int
        :return:
        """
        depth = len(path)
        _iter = self.connections_model.get_iter(path)
        o = self.connections_model.get_value(_iter, 0)

        if depth == 1:
            self.current_host = host = o
            if host.connected:
                self.current_host = None
                host.close()
            else:
                host.connect()
                if not host.connected:
                    return
            self.redraw_host(host, _iter, True)
            self.emma.current_query.set_current_host(self.current_host)

        elif depth == 2:

            def rfrs(arg):
                """
                :param arg: type
                """
                ctv, obj = arg
                new_tables = obj.refresh()
                ctv.redraw_db(obj, _iter, new_tables, True)
                ctv.emma.mainwindow.connections_tv_spinner.stop()
                ctv.emma.mainwindow.connections_tv_spinner.hide()
                ctv.show()

            self.current_host = o.host
            o.host.select_database(o)

            self.hide()
            self.emma.mainwindow.connections_tv_spinner.show()
            self.emma.mainwindow.connections_tv_spinner.start()
            gobject.idle_add(rfrs, (self, o))

            self.emma.current_query.set_current_db(o)

        elif depth == 3:
            self.current_host = host = o.db.host
            host.select_database(o.db)
            table = o
            self.emma.current_query.set_current_db(table.db)
            self.emma.main_notebook.add_generic_tab(widgets.TabTable(self.emma, table))
        else:
            print "No Handler for tree-depth", depth
        return

    def on_row_expanded(self, tv, _iter, path):
        """
        :param tv: gtk.TreeView
        :param _iter:
        :param path: str
        :return:
        """
        o = tv.get_model().get_value(_iter, 0)
        if len(path) > 3:
            return
        o.expanded = True

    def on_row_collapsed(self, tv, _iter, path):
        """
        :param tv: gtk.TreeView
        :param _iter:
        :param path: str
        :return:
        """
        o = tv.get_model().get_value(_iter, 0)
        if len(path) > 3:
            return
        o.expanded = False

    def on_connections_tv_cursor_changed(self, tv):
        """
        :param tv:
        :return:
        """
        path, column = tv.get_cursor()
        nb = self.emma.main_notebook
        if path is None:
            print "get_cursor() returned none. don't know which datebase is selected."
            return

        if len(path) == 3 and nb.get_current_page() == 3:
            pass

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
        """
        :param tv:
        :param event:
        :return:
        """
        if not event.button == 3:
            return False
        res = tv.get_path_at_pos(int(event.x), int(event.y))
        if not res or len(res[0]) == 1:
            self.pop_up_host.menu_modify_connection.set_sensitive(not not res)
            self.pop_up_host.menu_delete_connection.set_sensitive(not not res)
            connected_host = False
            if res:
                model = self.connections_model
                _iter = model.get_iter(res[0])
                host = model.get_value(_iter, 0)
                connected_host = host.connected
            self.pop_up_host.menu_new_database.set_sensitive(connected_host)
            self.pop_up_host.menu_refresh_host.set_sensitive(connected_host)
            self.pop_up_host.popup(None, None, None, event.button, event.time)
        elif len(res[0]) == 2:
            self.pop_up_database.popup(None, None, None, event.button, event.time)
        elif len(res[0]) == 3:
            self.pop_up_table.popup(None, None, None, event.button, event.time)

        return True

    def redraw_host(self, host, _iter, expand=False):
        """
        :param host:
        :param _iter:
        :param expand:
        """
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
        # print "redraw db", db.name
        """
        :param db:
        :param _iter:
        :param new_tables:
        :param force_expand:
        :return:
        """
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
            table.refresh()
            self.redraw_table(table, iterators[name])
            self.emma.process_events()

    def redraw_table(self, table, _iter):
        """
        :param table:
        :param _iter:
        """
        if table.expanded:
            self.expand_row(self.connections_model.get_path(_iter), False)
        i = self.connections_model.iter_children(_iter)
        while i and self.connections_model.iter_is_valid(i):
            self.connections_model.remove(i)
        for field in table.fields:
            self.connections_model.append(_iter, ((field.name, field.type),))

    def render_connections_pixbuf(self, column, cell, model, itr):
        """
        :param column:
        :param cell:
        :param model:
        :param itr:
        :return:
        """
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
            if o.is_table:
                cell.set_property("pixbuf", self.icons["table"])
            else:
                cell.set_property("pixbuf", self.icons["table_lightning"])
        elif d == 3:
            cell.set_property("pixbuf", self.icons["field"])

    def render_connections_text(self, column, cell, model, itr):
        """
        :param column:
        :param cell:
        :param model:
        :param itr:
        :return:
        """
        d = model.iter_depth(itr)
        o = model.get_value(itr, 0)
        if isinstance(o, str):
            cell.set_property("text", o)
            cell.set_property("weight-set", True)
            cell.set_property("weight", 400)
            return
        #
        #   HOST level
        #
        if d == 0:
            if o.connected:
                databases_count = o.databases.__len__()
                cell.set_property("text", "%s (%s)" % (o.name, databases_count))
                cell.set_property("weight-set", True)
                cell.set_property("weight", 700)
            else:
                cell.set_property("text", "%s" % o.name)
                cell.set_property("weight-set", True)
                cell.set_property("weight", 400)
        #
        #   DATABASE level
        #
        elif d == 1:
            cell.set_property("text", "%s" % o.name)
            cell.set_property("weight-set", True)
            cell.set_property("weight", 400)
        #
        #   TABLE level
        #
        elif d == 2:
            cell.set_property("text", "%s" % o.name)
            cell.set_property("weight-set", True)
            cell.set_property("weight", 400)
        #
        #   FIELD level
        #
        elif d == 3:
            cell.set_property("text", "%s %s" % (o[0], o[1]))
            cell.set_property("weight-set", True)
            cell.set_property("weight", 400)

    def load_icons(self):
        """
        Loads all needed icons
        """
        for icon in ["offline_host", "host", "db", "table", "table_lightning", "field"]:
            filename = os.path.join(icons_path, icon + ".png")
            try:
                self.icons[icon] = gtk.gdk.pixbuf_new_from_file(filename)
            except gobject.GError:
                print "could not load %r" % filename

    def add_mysql_host(self, name, hostname, port, user, password, database):
        """
        :param name: str
        :param hostname: str
        :param port: str
        :param user: str
        :param password: str
        :param database: str
        """
        from providers.mysql.MySqlHost import MySqlHost

        host = MySqlHost(
            self.emma.sql_log.log,
            self.emma.msg_log.log,
            name, hostname, port,
            user, password, database,
            self.emma.config.get("connect_timeout")
        )
        _iter = self.connections_model.append(None, [host])
        host.set_update_ui(self.redraw_host, _iter)

    def add_sqlite(self, filename):
        """
        :param filename: str
        """
        from providers.sqlite.SQLiteHost import SQLiteHost

        host = SQLiteHost(self.emma.sql_log.log, self.emma.msg_log.log, filename)
        _iter = self.connections_model.append(None, [host])
        host.set_update_ui(self.redraw_host, _iter)

    def get_current_table(self):
        """
        :return: ()
        """
        path, column = self.get_cursor()
        _iter = self.connections_model.get_iter(path)
        return path, column, _iter, self.connections_model.get_value(_iter, 0)

    def on_table_popup(self, popup, item):
        """
        :param popup:
        :param item:
        :return:
        """
        path, column, _iter, table = self.get_current_table()
        what = item.name

        if what == "refresh_table":
            table.refresh()
            self.redraw_table(table, _iter)
        elif what == "truncate_table":
            if not dialogs.confirm("truncate table",
                                   "do you really want to truncate the <b>%s</b> "
                                   "table in database <b>%s</b> on <b>%s</b>?" % (
                                           table.name,
                                           table.db.name,
                                           table.db.host.name
                                   ),
                                   self.emma.mainwindow):
                return
            if table.db.query("truncate `%s`" % table.name):
                table.refresh()
                self.redraw_table(table, _iter)
        elif what == "drop_table":
            if not dialogs.confirm("drop table",
                                   "do you really want to DROP the <b>%s</b> table in database "
                                   "<b>%s</b> on <b>%s</b>?" % (
                                           table.name,
                                           table.db.name,
                                           table.db.host.name
                                   ),
                                   self.emma.mainwindow):
                return
            db = table.db
            if db.query("drop table `%s`" % table.name):
                self.emma.events.trigger('on_table_dropped', table)
        elif what == "check_table":
            self.current_host = table.db.host
            self.current_host.select_database(table.db)
            self.emma.events.trigger('execute_query', None, "check table `%s`" % table.name)
        elif what == "repair_table":
            self.current_host = table.db.host
            self.current_host.select_database(table.db)
            self.emma.events.trigger('execute_query', None, "repair table `%s`" % table.name)

    def on_db_popup(self, popup, item):
        """
        :param popup:
        :param item:
        :return:
        """
        path, column = self.get_cursor()
        _iter = self.connections_model.get_iter(path)
        what = item.name
        db = self.connections_model.get_value(_iter, 0)

        if what == "refresh_database":
            new_tables = db.refresh()
            self.redraw_db(db, _iter, new_tables)
        elif what == "drop_database":
            if not dialogs.confirm("drop database",
                                   "do you really want to drop the <b>%s</b> "
                                   "database on <b>%s</b>?" % (
                                           db.name, db.host.name), self.emma.mainwindow):
                return
            host = db.host
            if host.query("drop database`%s`" % db.name):
                host.refresh()
                self.redraw_host(host, self.emma.connections_tv.get_host_iter(host))
        elif what == "new_table":
            name = dialogs.input_dialog("New table",
                                        "Please enter the name of the new table:",
                                        window=self.emma.mainwindow)
            if not name:
                return
            if db.query("create table `%s` (`%s_id` int primary key auto_increment)" % (name, name)):
                new_tables = db.refresh()
                self.redraw_db(db, self.emma.connections_tv.get_db_iter(db), new_tables)
        elif what == "check_tables":
            self.current_host = db.host
            self.current_host.select_database(db)
            db.refresh()
            self.emma.events.trigger(
                'execute_query',
                None,
                "check table %s" % (",".join(map(lambda s: "`%s`" % s, db.tables.keys()))))
        elif what == "repair_tables":
            self.current_host = db.host
            self.current_host.select_database(db)
            db.refresh()
            self.emma.events.trigger(
                'execute_query',
                None,
                "repair table %s" % (",".join(map(lambda s: "`%s`" % s, db.tables.keys()))))
        elif what == "list_tables":
            self.emma.main_notebook.add_tables_list_tab()

    def on_host_popup(self, popup, item):
        """
        :param popup:
        :param item:
        :return:
        """
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
            name = dialogs.input_dialog(
                "New database",
                "Please enter the name of the new database:",
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
            if not dialogs.confirm(
                    "Delete host", "Do you really want to drop the host <b>%s</b>?" % host.name,
                    self.emma.mainwindow):
                return
            host.close()
            self.connections_model.remove(_iter)
            if self.current_host == host:
                self.current_host = None
            del self.emma.config.config["connection_%s" % host.name]
            del host
            self.emma.config.save()
        elif what == "new_connection":
            self.connection_window.show("new")
        elif what == "show_processes":
            self.emma.main_notebook.add_process_list_tab(host)

    def get_connections_object_at_depth(self, obj, depth):
        """
        :param obj:
        :param depth:
        :return:
        """
        d = 0
        model = self.connections_model
        _iter = model.get_iter_first()
        while _iter:
            if d == depth and model.get_value(_iter, 0) == obj:
                return _iter
            if d < depth and model.iter_has_child(_iter):
                _iter = model.iter_children(_iter)
                d += 1
                continue
            new_iter = model.iter_next(_iter)
            if not new_iter:
                _iter = model.iter_parent(_iter)
                d -= 1
                _iter = model.iter_next(_iter)
            else:
                _iter = new_iter
        return None

    def get_db_iter(self, db):
        """
        :param db:
        :return:
        """
        return self.get_connections_object_at_depth(db, 1)

    def get_host_iter(self, host):
        """
        :param host:
        :return:
        """
        return self.get_connections_object_at_depth(host, 0)

