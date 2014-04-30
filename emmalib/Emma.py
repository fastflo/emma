from stat import *
import time
import gc
import pickle
import datetime
import bz2
import sql
import glib

import gtk
import gtk.gdk
import gtk.glade
import gobject

from query_regular_expression import *

from ConnectionTreeView import ConnectionsTreeView
from Config import Config
from QueryTab import QueryTab
from KeyMap import KeyMap
import dialogs
import widgets

from Constants import *


class Emma:
    def __init__(self):
        self.emma_path = emma_path
        self.sql = sql
        self.created_once = {}
        self.query_changed_listener = []
        self.queries = []
        self.stored_orders = {}
        self.query_count = 0
        self.glade_path = glade_path
        self.icons_path = icons_path
        self.glade_file = os.path.join(glade_path, "emma.glade")
        if not os.access(self.glade_file, os.R_OK):
            print self.glade_file, "not found!"
            sys.exit(-1)

        print "glade file: %r" % self.glade_file
        self.xml = gtk.glade.XML(self.glade_file)
        self.mainwindow = self.xml.get_widget("mainwindow")
        self.mainwindow.connect('destroy', lambda *args: gtk.main_quit())
        self.xml.signal_autoconnect(self)

        try:
            icon = gtk.gdk.pixbuf_new_from_file(os.path.join(icons_path, "emma.png"))
            self.mainwindow.set_icon(icon)
        except glib.GError:
            print "Icon not loaded"

        self.current_query = None

        # init dialogs
        self.about_dialog = dialogs.About()
        self.changelog_dialog = dialogs.ChangeLog(emma_path)
        self.execute_query_from_disk_dialog = False

        # init all notebooks
        self.message_notebook = self.xml.get_widget("message_notebook")
        self.main_notebook = self.xml.get_widget("main_notebook")

        # init Message log
        self.msg_log = widgets.TabMsgLog(self)
        self.message_notebook.prepend_page(self.msg_log, gtk.Label('Message Log'))

        # init SQL log
        self.sql_log = widgets.TabSqlLog(self)
        self.message_notebook.prepend_page(self.sql_log, gtk.Label('SQL Log'))

        self.blob_view = widgets.TabBlobView(self)
        self.message_notebook.append_page(self.blob_view, gtk.Label('Blob View'))

        # table view
        self.table_view = widgets.TabTable(self)
        #self.main_notebook.prepend_page(self.table_view, gtk.Label('Table'))

        # process list
        self.tableslist = widgets.TabTablesList(self)
        #self.main_notebook.prepend_page(self.tableslist, gtk.Label('Tables List'))

        # tables list
        self.processlist = widgets.TabProcessList(self)
        #self.main_notebook.prepend_page(self.processlist, gtk.Label('Process List'))

        # Local Search Window
        self.local_search_window = self.xml.get_widget("localsearch_window")
        self.local_search_entry = self.xml.get_widget("local_search_entry")
        self.local_search_entry.connect("activate", lambda *a: self.local_search_window.response(gtk.RESPONSE_OK))
        self.local_search_start_at_first_row = self.xml.get_widget("search_start_at_first_row")
        self.local_search_case_sensitive = self.xml.get_widget("search_case_sensitive")

        self.clipboard = gtk.Clipboard(gtk.gdk.display_get_default(), "CLIPBOARD")
        self.pri_clipboard = gtk.Clipboard(gtk.gdk.display_get_default(), "PRIMARY")

        self.field_edit = self.xml.get_widget("field_edit")
        self.field_edit_content = self.xml.get_widget("edit_field_content")

        self.tooltips = gtk.Tooltips()
        self.sort_timer_running = False
        self.execution_timer_running = False
        self.field_conditions_initialized = False
        self.current_host = None

        self.hosts = {}
        self.queries = []

        self.config = Config(self)
        self.config.load()

        self.connections_tv_container = self.xml.get_widget("connections_tv_container")
        self.connections_tv = ConnectionsTreeView(self)
        self.connections_tv_container.add(self.connections_tv)
        self.connections_tv.show()

        self.add_query_tab(QueryTab(self.main_notebook, self))

        self.key_map = KeyMap(self)
        self.mainwindow.connect('key_release_event', self.key_map.on_mainwindow_key_release_event)
        self.mainwindow.connect('key_press_event', self.key_map.on_mainwindow_key_press_event)

        self.first_template = None
        # keys = self.config.config.keys()
        # keys.sort()
        #
        # toolbar = self.xml.get_widget("query_toolbar")
        # toolbar.set_style(gtk.TOOLBAR_ICONS)
        # for child in toolbar.get_children():
        #     if not child.name.startswith("template_"):
        #         continue
        #     toolbar.remove(child)

        # template_count = 0
        # for name in keys:
        #     value = self.config.config[name]
        #     if not self.config.unpickled:
        #         prefix = "connection_"
        #         if name.startswith(prefix) and value == "::sqlite::":
        #             filename = name[len(prefix):]
        #             self.add_sqlite(filename)
        #             continue
        #         if name.startswith(prefix):
        #             v = value.split(",")
        #             port = ""
        #             p = v[0].rsplit(":", 1)
        #             if len(p) == 2:
        #                 port = p[1]
        #                 v[0] = p[0]
        #             self.add_mysql_host(name[len(prefix):], v[0], port, v[1], v[2], v[3])
        #             pass
        #
        #     prefix = "template"
        #     if name.startswith(prefix):
        #         value = value.replace("`$primary_key$`", "$primary_key$")
        #         value = value.replace("`$table$`", "$table$")
        #         value = value.replace("`$field_conditions$`", "$field_conditions$")
        #         self.config.config[name] = value
        #         if not self.first_template:
        #             self.first_template = value
        #         p = name.split("_", 1)
        #         template_count += 1
        #
        #         button = gtk.ToolButton(gtk.STOCK_EXECUTE)
        #         button.set_name("template_%d" % template_count)
        #         button.set_tooltip(self.tooltips, "%s\n%s" % (p[1], value))
        #         button.connect("clicked", self.on_template, value)
        #         toolbar.insert(button, -1)
        #         button.show()

        # menu = self.xml.get_widget("query_encoding_menu")
        # for child in menu.get_children():
        #     menu.remove(child)

        # for coding, index_desc in enumerate(self.config.codings):
        #     item = gtk.MenuItem(coding, False)
        #     item.connect("activate", self.on_query_encoding_changed, (coding, index_desc(0)))
        #     menu.append(item)
        #     item.show()

        if int(self.config.get("ping_connection_interval")) > 0:
            gobject.timeout_add(
                int(self.config.get("ping_connection_interval")) * 1000,
                self.on_connection_ping
            )
        self.init_plugins()

    def __getattr__(self, name):
        widget = self.xml.get_widget(name)
        if widget is None:
            raise AttributeError(name)
        return widget

    def on_reload_plugins_activate(self, *args):
        self.unload_plugins()
        self.load_plugins()

    def init_plugin(self, plugin):
        try:
            plugin_init = getattr(plugin, "plugin_init")
        except:
            return True
        plugin_init(self)

    def unload_plugin(self, plugin):
        try:
            plugin_unload = getattr(plugin, "plugin_unload")
            return plugin_unload()
        except:
            return True

    def load_plugins(self):
        def _load(_plugin_name):
            print "loading plugin %r" % _plugin_name
            if _plugin_name in self.plugins:
                plugin = reload(self.plugins[_plugin_name])
            else:
                plugin = __import__(_plugin_name)
            self.plugins[_plugin_name] = plugin
            self.init_plugin(plugin)
        for path in self.plugin_pathes:
            for plugin_name in os.listdir(path):
                plugin_dir = os.path.join(path, plugin_name)
                if not os.path.isdir(plugin_dir) or plugin_name[0] == ".":
                    continue
                #try:
                _load(plugin_name)
                #except Exception as e:
                #    print "!!!could not load plugin %r" % plugin_name, e.message

    def unload_plugins(self):
        """ not really an unload - i just asks the module to cleanup """
        for plugin_name, plugin in self.plugins.iteritems():
            #print "unloading plugin", plugin_name, "...",
            self.unload_plugin(plugin)
            #print "done"

    def init_plugins(self):
        plugins_pathes = [
            # os.path.join(self.config.config_path, "plugins"),
            os.path.join(emma_path, "plugins")
        ]
        self.plugin_pathes = []
        self.plugins = {}
        for path in plugins_pathes:
            if not os.path.isdir(path):
                print "plugins-dir %r does not exist" % path
                continue
            if not path in sys.path:
                sys.path.insert(0, path)
            self.plugin_pathes.append(path)
        self.load_plugins()

    def add_query_tab(self, qt):
        self.query_count += 1
        self.current_query = qt
        self.queries.append(qt)
        qt.set_query_encoding(self.config.get("db_encoding"))
        qt.set_query_font(self.config.get("query_text_font"))
        qt.set_result_font(self.config.get("query_result_font"))
        if self.config.get_bool("query_text_wrap"):
            qt.set_wrap_mode(gtk.WRAP_WORD)
        else:
            qt.set_wrap_mode(gtk.WRAP_NONE)
        qt.set_current_host(self.current_host)

        tab_label_hbox = gtk.HBox()
        tab_label_label = gtk.Label('Query')
        tab_label_label.show()
        tab_label_ebox = gtk.EventBox()
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_CLOSE, 1)
        img.show()
        tab_label_ebox.add(img)
        tab_label_ebox.show()
        tab_label_ebox.connect('button_release_event', self.on_closequery_label_button_clicked)

        tab_label_hbox.pack_start(tab_label_label)
        tab_label_hbox.pack_end(tab_label_ebox)
        tab_label_hbox.show()

        new_page_index = self.main_notebook.append_page(qt.xml.get_widget('first_query'), tab_label_hbox)
        qt.page_index = new_page_index
        self.main_notebook.set_current_page(new_page_index)
        self.current_query.textview.grab_focus()

    def on_closequery_label_button_clicked(self, button, event):
        self.close_query(None)

    def on_connection_ping(self):
        _iter = self.connections_tv.connections_model.get_iter_root()
        while _iter:
            host = self.connections_tv.connections_model.get_value(_iter, 0)
            if host.connected:
                if not host.ping():
                    print "...error! reconnect seems to fail!"
            _iter = self.connections_tv.connections_model.iter_next(_iter)
        return True

    # def search_query_end(self, text, _start):
    #     try:
    #         r = self.query_end_re
    #     except:
    #         r = self.query_end_re = re.compile(r'("(?:[^\\]|\\.)*?")|(\'(?:[^\\]|\\.)*?\')|(`(?:[^\\]|\\.)*?`)|(;)')
    #     while 1:
    #         result = re.search(r, text[_start:])
    #         if not result:
    #             return None
    #
    #         _start += result.end()
    #         if result.group(4):
    #             return _start

    # def get_field_list(self, s):
    #     # todo USE IT!
    #     fields = []
    #     _start = 0
    #     ident = None
    #     while 1:
    #         item = []
    #         while 1:
    #             ident, end = self.read_expression(s[_start:])
    #             if not ident:
    #                 break
    #             if ident == ",":
    #                 break
    #             if ident[0] == "`":
    #                 ident = ident[1:-1]
    #             item.append(ident)
    #             _start += end
    #         if len(item) == 1:
    #             fields.append(item[0])
    #         else:
    #             fields.append(item)
    #         if not ident:
    #             break
    #     print "found fields:", fields
    #     return fields

    def on_reload_self_activate(self, item):
        pass

    def on_message_notebook_switch_page(self, nb, pointer, page):
        if self.current_query:
            self.current_query.on_query_view_cursor_changed(self.current_query.treeview)

    def on_execute_query_from_disk_activate(self, button, filename=None):
        if not self.current_host:
            dialogs.show_message("execute query from disk", "no host selected!")
            return
        if not self.execute_query_from_disk_dialog:
            self.execute_query_from_disk_dialog = dialogs.ExecuteQueryFromDisk(self)
        self.execute_query_from_disk_dialog.show()

    def get_widget(self, name):
        return self.assign_once("widget_%s" % name, self.xml.get_widget, name)

    def assign_once(self, name, creator, *args):
        try:
            return self.created_once[name]
        except:
            obj = creator(*args)
            self.created_once[name] = obj
            return obj

    def on_save_workspace_activate(self, button):
        d = self.assign_once(
            "save workspace dialog",
            gtk.FileChooserDialog, "save workspace", self.mainwindow, gtk.FILE_CHOOSER_ACTION_SAVE,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))

        d.set_default_response(gtk.RESPONSE_ACCEPT)
        answer = d.run()
        d.hide()
        if not answer == gtk.RESPONSE_ACCEPT:
            return
        filename = d.get_filename()
        if os.path.exists(filename):
            if not os.path.isfile(filename):
                dialogs.show_message("save workspace", "%s already exists and is not a file!" % filename)
                return
            if not dialogs.confirm(
                    "overwrite file?",
                    "%s already exists! do you want to overwrite it?" % filename, self.mainwindow):
                return
        try:
            fp = file(filename, "wb")
            pickle.dump(self, fp)
            fp.close()
        except:
            dialogs.show_message(
                "save workspace",
                "error writing workspace to file %s: %s/%s" % (filename, sys.exc_type, sys.exc_value))

    def on_restore_workspace_activate(self, button):
        global new_instance
        d = self.assign_once(
            "restore workspace dialog",
            gtk.FileChooserDialog, "restore workspace", self.mainwindow, gtk.FILE_CHOOSER_ACTION_OPEN,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))

        d.set_default_response(gtk.RESPONSE_ACCEPT)
        answer = d.run()
        d.hide()
        if not answer == gtk.RESPONSE_ACCEPT:
            return
        filename = d.get_filename()
        if not os.path.exists(filename):
            dialogs.show_message("restore workspace", "%s does not exists!" % filename)
            return
        if not os.path.isfile(filename):
            dialogs.show_message("restore workspace", "%s exists, but is not a file!" % filename)
            return

        try:
            fp = file(filename, "rb")
            print "i am unpickling:", self
            new_instance = pickle.load(fp)
            print "got new instance:", new_instance
            fp.close()
        except:
            dialogs.show_message(
                "restore workspace",
                "error restoring workspace from file %s: %s/%s" % (filename, sys.exc_type, sys.exc_value))
        self.mainwindow.destroy()

    # def __setstate__(self, state):
    #     self.state = state

    def query_changed(self, q):
        for f in self.query_changed_listener:
            try:
                f(q)
            except:
                print "query_change_listener %r had exception" % f

    def close_query(self, button):
        if len(self.queries) == 1:
            return
        self.current_query.destroy()

        i = self.queries.index(self.current_query)
        del self.queries[i]
        self.current_query = None

        self.main_notebook.remove_page(self.main_notebook.get_current_page())
        gc.collect()

    def on_fc_reset_clicked(self, button):
        for i in range(self.fc_count):
            self.fc_entry[i].set_text("")
            if i == 0:
                self.fc_combobox[i].set_active(0)
                self.fc_op_combobox[i].set_active(0)
            else:
                self.fc_combobox[i].set_active(-1)
                self.fc_op_combobox[i].set_active(-1)
            if i:
                self.fc_logic_combobox[i - 1].set_active(0)

    def on_quit_activate(self, item):
        gtk.main_quit()

    def on_about_activate(self, item):
        self.about_dialog.run()
        self.about_dialog.hide()

    def on_changelog_activate(self, item):
        self.changelog_dialog.show()

    def main_notebook_on_change_page(self, np, pointer, page):
        for q in self.queries:
            if q.page_index == page:
                self.current_query = q
                q.on_query_db_eventbox_button_press_event(None, None)
                self.query_changed(q)
                return

        # if page == 2:
        #     self.tableslist.redraw()
        #     return
        # path, column = self.connections_tv.get_cursor()
        # if not path:
        #     return
        # if len(path) == 3 and page == 3:
        #     self.table_view.update(path)

    def get_current_table(self):
        path, column = self.connections_tv.get_cursor()
        _iter = self.connections_tv.connections_model.get_iter(path)
        return path, column, _iter, self.connections_tv.connections_model.get_value(_iter, 0)

    def get_db_iter(self, db):
        return self.get_connections_object_at_depth(db, 1)

    def get_host_iter(self, host):
        return self.get_connections_object_at_depth(host, 0)

    def get_connections_object_at_depth(self, obj, depth):
        d = 0
        model = self.connections_tv.connections_model
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

    def on_query_popup(self, item):
        q = self.current_query
        path, column = q.treeview.get_cursor()
        _iter = q.model.get_iter(path)

        if item.name == "copy_field_value":
            col_max = q.model.get_n_columns()
            for col_num in range(col_max):
                if column == q.treeview.get_column(col_num):
                    break
            else:
                print "column not found!"
                return
            value = q.model.get_value(_iter, col_num)
            self.clipboard.set_text(value)
            self.pri_clipboard.set_text(value)
        elif item.name == "copy_record_as_csv":
            col_max = q.model.get_n_columns()
            value = ""
            for col_num in range(col_max):
                if value:
                    value += self.config.get("copy_record_as_csv_delim")
                v = q.model.get_value(_iter, col_num)
                if not v is None:
                    value += v
            self.clipboard.set_text(value)
            self.pri_clipboard.set_text(value)
        elif item.name == "copy_record_as_quoted_csv":
            col_max = q.model.get_n_columns()
            value = ""
            for col_num in range(col_max):
                if value:
                    value += self.config.get("copy_record_as_csv_delim")
                v = q.model.get_value(_iter, col_num)
                if not v is None:
                    v = v.replace("\"", "\\\"")
                    value += '"%s"' % v
            self.clipboard.set_text(value)
            self.pri_clipboard.set_text(value)
        elif item.name == "copy_column_as_csv":
            col_max = q.model.get_n_columns()
            for col_num in range(col_max):
                if column == q.treeview.get_column(col_num):
                    break
            else:
                print "column not found!"
                return
            value = ""
            _iter = q.model.get_iter_first()
            while _iter:
                if value:
                    value += self.config.get("copy_record_as_csv_delim")
                v = q.model.get_value(_iter, col_num)
                if not v is None:
                    value += v
                _iter = q.model.iter_next(_iter)
            self.clipboard.set_text(value)
            self.pri_clipboard.set_text(value)
        elif item.name == "copy_column_as_quoted_csv":
            col_max = q.model.get_n_columns()
            for col_num in range(col_max):
                if column == q.treeview.get_column(col_num):
                    break
            else:
                print "column not found!"
                return
            value = ""
            _iter = q.model.get_iter_first()
            while _iter:
                if value:
                    value += self.config.get("copy_record_as_csv_delim")
                v = q.model.get_value(_iter, col_num)
                if not v is None:
                    v = v.replace("\"", "\\\"")
                    value += '"%s"' % v
                _iter = q.model.iter_next(_iter)
            self.clipboard.set_text(value)
            self.pri_clipboard.set_text(value)
        elif item.name == "copy_column_names":
            value = ""
            for col in q.treeview.get_columns():
                if value:
                    value += self.config.get("copy_record_as_csv_delim")
                value += col.get_title().replace("__", "_")
            self.clipboard.set_text(value)
            self.pri_clipboard.set_text(value)
        elif item.name == "set_value_null":
            col_max = q.model.get_n_columns()
            for col_num in range(col_max):
                if column == q.treeview.get_column(col_num):
                    break
            else:
                print "column not found!"
                return
            table, where, field, value, row_iter = q.get_unique_where(q.last_source, path, col_num)
            update_query = "update `%s` set `%s`=NULL where %s limit 1" % (table, field, where)
            if self.current_host.query(update_query, encoding=q.encoding):
                q.model.set_value(row_iter, col_num, None)
        elif item.name == "set_value_now":
            col_max = q.model.get_n_columns()
            for col_num in range(col_max):
                if column == q.treeview.get_column(col_num):
                    break
            else:
                print "column not found!"
                return
            table, where, field, value, row_iter = q.get_unique_where(q.last_source, path, col_num)
            update_query = "update `%s` set `%s`=now() where %s limit 1" % (table, field, where)
            if not self.current_host.query(update_query, encoding=q.encoding):
                return
            self.current_host.query("select `%s` from `%s` where %s limit 1" % (field, table, where))
            result = self.current_host.handle.store_result().fetch_row(0)
            if len(result) < 1:
                print "error: can't find modfied row!?"
                return
            q.model.set_value(row_iter, col_num, result[0][0])
        elif item.name == "set_value_unix_timestamp":
            col_max = q.model.get_n_columns()
            for col_num in range(col_max):
                if column == q.treeview.get_column(col_num):
                    break
            else:
                print "column not found!"
                return
            table, where, field, value, row_iter = q.get_unique_where(q.last_source, path, col_num)
            update_query = "update `%s` set `%s`=unix_timestamp(now()) where %s limit 1" % (table, field, where)
            if not self.current_host.query(update_query, encoding=q.encoding):
                return
            self.current_host.query("select `%s` from `%s` where %s limit 1" % (field, table, where))
            result = self.current_host.handle.store_result().fetch_row(0)
            if len(result) < 1:
                print "error: can't find modfied row!?"
                return
            q.model.set_value(row_iter, col_num, result[0][0])
        elif item.name == "set_value_as_password":
            col_max = q.model.get_n_columns()
            for col_num in range(col_max):
                if column == q.treeview.get_column(col_num):
                    break
            else:
                print "column not found!"
                return
            table, where, field, value, row_iter = q.get_unique_where(q.last_source, path, col_num)
            update_query = "update `%s` set `%s`=password('%s') where %s limit 1" % (table, field,
                                                                                     self.current_host.escape(value),
                                                                                     where)
            if not self.current_host.query(update_query, encoding=q.encoding):
                return
            self.current_host.query("select `%s` from `%s` where %s limit 1" % (field, table, where))
            result = self.current_host.handle.store_result().fetch_row(0)
            if len(result) < 1:
                print "error: can't find modfied row!?"
                return
            q.model.set_value(row_iter, col_num, result[0][0])
        elif item.name == "set_value_to_sha":
            col_max = q.model.get_n_columns()
            for col_num in range(col_max):
                if column == q.treeview.get_column(col_num):
                    break
            else:
                print "column not found!"
                return
            table, where, field, value, row_iter = q.get_unique_where(q.last_source, path, col_num)
            update_query = "update `%s` set `%s`=sha1('%s') where %s limit 1" % (table, field,
                                                                                 self.current_host.escape(value),
                                                                                 where)
            if not self.current_host.query(update_query, encoding=q.encoding):
                return
            self.current_host.query("select `%s` from `%s` where %s limit 1" % (field, table, where))
            result = self.current_host.handle.store_result().fetch_row(0)
            if len(result) < 1:
                print "error: can't find modfied row!?"
                return
            q.model.set_value(row_iter, col_num, result[0][0])

    def on_template(self, button, t):
        current_table = self.get_selected_table()
        current_fc_table = current_table

        if t.find("$table$") != -1:
            if not current_table:
                dialogs.show_message(
                    "info",
                    "no table selected!\nyou can't execute a template with $table$ in it, "
                    "if you have no table selected!")
                return
            t = t.replace("$table$", self.current_host.escape_table(current_table.name))

        pos = t.find("$primary_key$")
        if pos != -1:
            if not current_table:
                dialogs.show_message(
                    "info",
                    "no table selected!\nyou can't execute a template with $primary_key$ in it, "
                    "if you have no table selected!")
                return
            if not current_table.fields:
                dialogs.show_message(
                    "info",
                    "sorry, can't execute this template, because table '%s' has no fields!" % current_table.name)
                return
            # is the next token desc or asc?
            result = re.search("(?i)[ \t\r\n]*(de|a)sc", t[pos:])
            order_dir = ""
            if result:
                o = result.group(1).lower()
                if o == "a":
                    order_dir = "asc"
                else:
                    order_dir = "desc"

            replace = ""
            while 1:
                primary_key = ""
                for name in current_table.field_order:
                    props = current_table.fields[name]
                    if props[3] != "PRI":
                        continue
                    if primary_key:
                        primary_key += " " + order_dir + ", "
                    primary_key += self.current_host.escape_field(name)
                if primary_key:
                    replace = primary_key
                    break
                key = ""
                for name in current_table.field_order:
                    props = current_table.fields[name]
                    if props[3] != "UNI":
                        continue
                    if key:
                        key += " " + order_dir + ", "
                    key += self.current_host.escape_field(name)
                if key:
                    replace = key
                    break
                replace = self.current_host.escape_field(current_table.field_order[0])
                break
            t = t.replace("$primary_key$", replace)

        if t.find("$field_conditions$") != -1:
            if not self.field_conditions_initialized:
                self.field_conditions_initialized = True
                self.fc_count = 4
                self.fc_window = self.xml.get_widget("field_conditions")
                table = self.xml.get_widget("fc_table")
                table.resize(1 + self.fc_count, 4)
                self.fc_entry = []
                self.fc_combobox = []
                self.fc_op_combobox = []
                self.fc_logic_combobox = []
                for i in range(self.fc_count):
                    self.fc_entry.append(gtk.Entry())
                    self.fc_entry[i].connect("activate", lambda *e: self.fc_window.response(gtk.RESPONSE_OK))
                    self.fc_combobox.append(gtk.combo_box_new_text())
                    self.fc_op_combobox.append(gtk.combo_box_new_text())
                    self.fc_op_combobox[i].append_text("=")
                    self.fc_op_combobox[i].append_text("<")
                    self.fc_op_combobox[i].append_text(">")
                    self.fc_op_combobox[i].append_text("!=")
                    self.fc_op_combobox[i].append_text("LIKE")
                    self.fc_op_combobox[i].append_text("NOT LIKE")
                    self.fc_op_combobox[i].append_text("ISNULL")
                    self.fc_op_combobox[i].append_text("NOT ISNULL")
                    if i:
                        self.fc_logic_combobox.append(gtk.combo_box_new_text())
                        self.fc_logic_combobox[i - 1].append_text("disabled")
                        self.fc_logic_combobox[i - 1].append_text("AND")
                        self.fc_logic_combobox[i - 1].append_text("OR")
                        table.attach(self.fc_logic_combobox[i - 1], 0, 1, i + 1, i + 2)
                        self.fc_logic_combobox[i - 1].show()
                    table.attach(self.fc_combobox[i], 1, 2, i + 1, i + 2)
                    table.attach(self.fc_op_combobox[i], 2, 3, i + 1, i + 2)
                    table.attach(self.fc_entry[i], 3, 4, i + 1, i + 2)
                    self.fc_combobox[i].show()
                    self.fc_op_combobox[i].show()
                    self.fc_entry[i].show()
            if not current_table:
                dialogs.show_message(
                    "info",
                    "no table selected!\nyou can't execute a template with "
                    "$field_conditions$ in it, if you have no table selected!")
                return

            last_field = []
            for i in range(self.fc_count):
                last_field.append(self.fc_combobox[i].get_active_text())
                self.fc_combobox[i].get_model().clear()
                if i:
                    self.fc_logic_combobox[i - 1].set_active(0)
            fc = 0
            for field_name in current_table.field_order:
                for k in range(self.fc_count):
                    self.fc_combobox[k].append_text(field_name)
                    if last_field[k] == field_name:
                        self.fc_combobox[k].set_active(fc)
                fc += 1
            if not self.fc_op_combobox[0].get_active_text():
                self.fc_op_combobox[0].set_active(0)
            if not self.fc_combobox[0].get_active_text():
                self.fc_combobox[0].set_active(0)

            answer = self.fc_window.run()
            self.fc_window.hide()
            if answer != gtk.RESPONSE_OK:
                return

            def field_operator_value(field, op, value):
                if op == "ISNULL":
                    return "isnull(`%s`)" % field
                if op == "NOT ISNULL":
                    return "not isnull(`%s`)" % field
                eval_kw = "eval: "
                if value.startswith(eval_kw):
                    return "`%s` %s %s" % (field, op, value[len(eval_kw):])
                return "%s %s '%s'" % (self.current_host.escape_field(field), op, self.current_host.escape(value))

            conditions = "%s" % (
                field_operator_value(
                    self.fc_combobox[0].get_active_text(),
                    self.fc_op_combobox[0].get_active_text(),
                    self.fc_entry[0].get_text()
                )
            )
            for i in range(1, self.fc_count):
                if self.fc_logic_combobox[i - 1].get_active_text() == "disabled" \
                        or self.fc_combobox[i].get_active_text() == "" \
                        or self.fc_op_combobox[i].get_active_text() == "":
                    continue
                conditions += " %s %s" % (
                    self.fc_logic_combobox[i - 1].get_active_text(),
                    field_operator_value(
                        self.fc_combobox[i].get_active_text(),
                        self.fc_op_combobox[i].get_active_text(),
                        self.fc_entry[i].get_text()
                    )
                )
            t = t.replace("$field_conditions$", conditions)

        try:
            new_order = self.stored_orders[self.current_host.current_db.name][current_table.name]
            print "found stored order: %r" % (new_order, )
            query = t
            try:
                r = self.query_order_re
            except:
                r = self.query_order_re = re.compile(re_src_query_order)
            match = re.search(r, query)
            if match:
                before, order, after = match.groups()
                order = ""
                addition = ""
            else:
                match = re.search(re_src_after_order, query)
                if not match:
                    before = query
                    after = ""
                else:
                    before = query[0:match.start()]
                    after = match.group()
                addition = "\norder by\n\t"
            order = ""
            for col, o in new_order:
                if order:
                    order += ",\n\t"
                order += self.current_host.escape_field(col)
                if not o:
                    order += " desc"
            if order:
                new_query = ''.join([before, addition, order, after])
            else:
                new_query = re.sub("(?i)order[ \r\n\t]+by[ \r\n\t]+", "", before + after)

            t = new_query
        except:
            pass
        self.current_query.on_execute_query_clicked(None, t)

    def render_mysql_string(self, column, cell, model, _iter, _id):
        o = model.get_value(_iter, _id)
        if not o is None:
            cell.set_property("background", None)
            if len(o) < 256:
                cell.set_property("text", o)
                cell.set_property("editable", True)
            else:
                cell.set_property("text", o[0:256] + "...")
                cell.set_property("editable", False)
        else:
            cell.set_property("background", self.config.get("null_color"))
            cell.set_property("text", "")
            cell.set_property("editable", True)

    def on_reread_config_activate(self, item):
        self.config.load()

    def on_query_encoding_changed(self, menuitem, data):
        self.current_query.set_query_encoding(data[0])

    def process_events(self):
        while gtk.events_pending():
            gtk.main_iteration(False)

    def get_selected_table(self):
        path, column = self.connections_tv.get_cursor()
        depth = len(path)
        _iter = self.connections_tv.connections_model.get_iter(path)
        if depth == 3:
            return self.connections_tv.connections_model.get_value(_iter, 0)
        return None



