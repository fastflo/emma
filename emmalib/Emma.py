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

import gtk
import glib
import gobject

import gtk.gdk
import gtk.glade

import dialogs
import widgets
from Config import Config
from KeyMap import KeyMap
from Constants import *
from ConnectionTreeView import ConnectionsTreeView
from EventsManager import EventsManager


class Emma:
    """
    Main Emma Class
    """
    def __init__(self):

        self.created_once = {}
        self.stored_orders = {}
        self.tooltips = gtk.Tooltips()
        self.sort_timer_running = False
        self.execution_timer_running = False
        # self.field_conditions_initialized = False
        self.current_host = None

        self.plugin_pathes = []
        self.plugins = {}

        self.hosts = {}

        self.clipboard = gtk.Clipboard(gtk.gdk.display_get_default(), "CLIPBOARD")
        self.pri_clipboard = gtk.Clipboard(gtk.gdk.display_get_default(), "PRIMARY")

        self.config = Config(self)
        self.config.load()

        self.execute_query_from_disk_dialog = False

        #
        #   Vars for use in start
        #
        self.glade_file = None
        self.xml = None
        self.key_map = None
        self.mainwindow = None
        self.current_query = None
        self.message_notebook = None
        self.main_notebook = None
        self.msg_log = None
        self.sql_log = None
        self.blob_view = None
        self.connections_tv = None
        self.local_search_window = None
        self.local_search_entry = None
        self.local_search_start_at_first_row = None
        self.local_search_case_sensitive = None
        #
        # init dialogs
        #
        self.about_dialog = dialogs.About()
        self.changelog_dialog = dialogs.ChangeLog()
        #
        # init event manager
        #
        self.events = EventsManager()

    def start(self):
        """
        Start Emma process
        """
        self.glade_file = os.path.join(glade_path, "emma.glade")
        if not os.access(self.glade_file, os.R_OK):
            print self.glade_file, "not found!"
            sys.exit(-1)

        print "glade file: %r" % self.glade_file
        self.xml = gtk.glade.XML(self.glade_file)
        self.xml.signal_autoconnect(self)

        self.mainwindow = widgets.MainWindow(self)
        self.mainwindow.connect('destroy', lambda *args: gtk.main_quit())

        self.key_map = KeyMap(self)

        try:
            icon = gtk.gdk.pixbuf_new_from_file(os.path.join(icons_path, "emma.png"))
            self.mainwindow.set_icon(icon)
        except glib.GError:
            print "Icon not loaded"

        # init all notebooks
        self.message_notebook = self.mainwindow.message_notebook
        self.main_notebook = self.mainwindow.main_notebook

        # init Message log
        self.msg_log = widgets.TabMsgLog(self)
        self.message_notebook.prepend_page(self.msg_log, gtk.Label('Message Log'))

        # init SQL log
        self.sql_log = widgets.TabSqlLog(self)
        self.message_notebook.prepend_page(self.sql_log, gtk.Label('SQL Log'))

        self.blob_view = widgets.TabBlobView(self)
        self.message_notebook.append_page(self.blob_view, gtk.Label('Blob View'))

        # Local Search Window
        self.local_search_window = self.xml.get_widget("localsearch_window")
        self.local_search_entry = self.xml.get_widget("local_search_entry")
        self.local_search_entry.connect(
            "activate",
            lambda *a: self.local_search_window.response(gtk.RESPONSE_OK)
        )
        self.local_search_start_at_first_row = self.xml.get_widget("search_start_at_first_row")
        self.local_search_case_sensitive = self.xml.get_widget("search_case_sensitive")

        # self.field_edit = self.xml.get_widget("field_edit")
        # self.field_edit_content = self.xml.get_widget("edit_field_content")

        self.connections_tv = ConnectionsTreeView(self)
        self.mainwindow.connections_tv_container.add(self.connections_tv)
        self.connections_tv.show()

        self.main_notebook.add_query_tab()

        if int(self.config.get("ping_connection_interval")) > 0:
            gobject.timeout_add(
                int(self.config.get("ping_connection_interval")) * 1000,
                self.on_connection_ping
            )
        self.init_plugins()

    def init_plugin(self, plugin):
        """
        Init Plugin
        @param plugin: module
        @return: bool
        """
        try:
            plugin_init = getattr(plugin, "plugin_init")
        except:
            return True
        plugin_init(self)

    def unload_plugin(self, plugin):
        """
        @param plugin: module
        @return: bool
        """
        try:
            plugin_unload = getattr(plugin, "plugin_unload")
            return plugin_unload()
        except:
            return True

    def load_plugins(self):
        """
        Load plugins
        """
        def _load(_plugin_name):
            print "loading plugin %r" % _plugin_name
            if _plugin_name in self.plugins:
                plugin = reload(self.plugins[_plugin_name])
            else:
                plugin = __import__(_plugin_name)

            print "PLUGIN:", plugin
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
        """
        not really an unload - i just asks the module to cleanup
        """
        for plugin_name, plugin in self.plugins.iteritems():
            self.unload_plugin(plugin)

    def init_plugins(self):
        """
        Init plugins
        """
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

    # TODO: move to providers
    def on_connection_ping(self):
        """
        Ping connection
        @return: bool
        """
        _iter = self.connections_tv.connections_model.get_iter_root()
        while _iter:
            host = self.connections_tv.connections_model.get_value(_iter, 0)
            if host.connected:
                if not host.ping():
                    print "...error! reconnect seems to fail!"
            _iter = self.connections_tv.connections_model.iter_next(_iter)
        return True

    def toggle_connections_tv(self, _, window):
        """
        @param _: gtk.CheckMenuItem
        @param window: MainWindow
        """
        window.connections_tv_container.get_parent().set_visible(
            not window.connections_tv_container.get_parent().get_visible())

    def toggle_message_notebook(self, _, window):
        """
        @param _: gtk.CheckMenuItem
        @param window: MainWindow
        """
        window.message_notebook.set_visible(
            not window.message_notebook.get_visible())

    def on_execute_query_from_disk_activate(self, button, filename=None):
        """
        @param button: gtk.Button
        @param filename: str
        @return:
        """
        if not self.connections_tv.current_host:
            dialogs.show_message("execute query from disk", "no host selected!")
            return
        if not self.execute_query_from_disk_dialog:
            self.execute_query_from_disk_dialog = dialogs.ExecuteQueryFromDisk(self)
        self.execute_query_from_disk_dialog.show()

    def assign_once(self, name, creator, *args):
        """
        Singletone maker
        @param name: string
        @param creator: type
        @param args: []
        @return:
        """
        try:
            return self.created_once[name]
        except:
            obj = creator(*args)
            self.created_once[name] = obj
            return obj

    # def on_save_workspace_activate(self, button):
    #     d = self.assign_once(
    #         "save workspace dialog",
    #         gtk.FileChooserDialog, "save workspace", self.mainwindow, gtk.FILE_CHOOSER_ACTION_SAVE,
    #         (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))
    #
    #     d.set_default_response(gtk.RESPONSE_ACCEPT)
    #     answer = d.run()
    #     d.hide()
    #     if not answer == gtk.RESPONSE_ACCEPT:
    #         return
    #     filename = d.get_filename()
    #     if os.path.exists(filename):
    #         if not os.path.isfile(filename):
    #             dialogs.show_message("save workspace", "%s already exists and is not a file!" % filename)
    #             return
    #         if not dialogs.confirm(
    #                 "overwrite file?",
    #                 "%s already exists! do you want to overwrite it?" % filename, self.mainwindow):
    #             return
    #     try:
    #         fp = file(filename, "wb")
    #         pickle.dump(self, fp)
    #         fp.close()
    #     except:
    #         dialogs.show_message(
    #             "save workspace",
    #             "error writing workspace to file %s: %s/%s" % (filename, sys.exc_type, sys.exc_value))
    #
    # def on_restore_workspace_activate(self, button):
    #     global new_instance
    #     d = self.assign_once(
    #         "restore workspace dialog",
    #         gtk.FileChooserDialog, "restore workspace", self.mainwindow, gtk.FILE_CHOOSER_ACTION_OPEN,
    #         (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))
    #
    #     d.set_default_response(gtk.RESPONSE_ACCEPT)
    #     answer = d.run()
    #     d.hide()
    #     if not answer == gtk.RESPONSE_ACCEPT:
    #         return
    #     filename = d.get_filename()
    #     if not os.path.exists(filename):
    #         dialogs.show_message("restore workspace", "%s does not exists!" % filename)
    #         return
    #     if not os.path.isfile(filename):
    #         dialogs.show_message("restore workspace", "%s exists, but is not a file!" % filename)
    #         return
    #
    #     try:
    #         fp = file(filename, "rb")
    #         print "i am unpickling:", self
    #         new_instance = pickle.load(fp)
    #         print "got new instance:", new_instance
    #         fp.close()
    #     except:
    #         dialogs.show_message(
    #             "restore workspace",
    #             "error restoring workspace from file %s: %s/%s" % (filename, sys.exc_type, sys.exc_value))
    #     self.mainwindow.destroy()

    # def __setstate__(self, state):
    #     self.state = state

    # def on_fc_reset_clicked(self, button):
    #     for i in range(self.fc_count):
    #         self.fc_entry[i].set_text("")
    #         if i == 0:
    #             self.fc_combobox[i].set_active(0)
    #             self.fc_op_combobox[i].set_active(0)
    #         else:
    #             self.fc_combobox[i].set_active(-1)
    #             self.fc_op_combobox[i].set_active(-1)
    #         if i:
    #             self.fc_logic_combobox[i - 1].set_active(0)

    # def on_template(self, button, t):
    #     current_table = self.get_selected_table()
    #     current_fc_table = current_table
    #
    #     if t.find("$table$") != -1:
    #         if not current_table:
    #             dialogs.show_message(
    #                 "info",
    #                 "no table selected!\nyou can't execute a template with $table$ in it, "
    #                 "if you have no table selected!")
    #             return
    #         t = t.replace("$table$", self.current_host.escape_table(current_table.name))
    #
    #     pos = t.find("$primary_key$")
    #     if pos != -1:
    #         if not current_table:
    #             dialogs.show_message(
    #                 "info",
    #                 "no table selected!\nyou can't execute a template with $primary_key$ in it, "
    #                 "if you have no table selected!")
    #             return
    #         if not current_table.fields:
    #             dialogs.show_message(
    #                 "info",
    #                 "sorry, can't execute this template, because table '%s' has no fields!" % current_table.name)
    #             return
    #         # is the next token desc or asc?
    #         result = re.search("(?i)[ \t\r\n]*(de|a)sc", t[pos:])
    #         order_dir = ""
    #         if result:
    #             o = result.group(1).lower()
    #             if o == "a":
    #                 order_dir = "asc"
    #             else:
    #                 order_dir = "desc"
    #
    #         replace = ""
    #         while 1:
    #             primary_key = ""
    #             for name in current_table.field_order:
    #                 props = current_table.fields[name]
    #                 if props[3] != "PRI":
    #                     continue
    #                 if primary_key:
    #                     primary_key += " " + order_dir + ", "
    #                 primary_key += self.current_host.escape_field(name)
    #             if primary_key:
    #                 replace = primary_key
    #                 break
    #             key = ""
    #             for name in current_table.field_order:
    #                 props = current_table.fields[name]
    #                 if props[3] != "UNI":
    #                     continue
    #                 if key:
    #                     key += " " + order_dir + ", "
    #                 key += self.current_host.escape_field(name)
    #             if key:
    #                 replace = key
    #                 break
    #             replace = self.current_host.escape_field(current_table.field_order[0])
    #             break
    #         t = t.replace("$primary_key$", replace)
    #
    #     if t.find("$field_conditions$") != -1:
    #         if not self.field_conditions_initialized:
    #             self.field_conditions_initialized = True
    #             self.fc_count = 4
    #             self.fc_window = self.xml.get_widget("field_conditions")
    #             table = self.xml.get_widget("fc_table")
    #             table.resize(1 + self.fc_count, 4)
    #             self.fc_entry = []
    #             self.fc_combobox = []
    #             self.fc_op_combobox = []
    #             self.fc_logic_combobox = []
    #             for i in range(self.fc_count):
    #                 self.fc_entry.append(gtk.Entry())
    #                 self.fc_entry[i].connect("activate", lambda *e: self.fc_window.response(gtk.RESPONSE_OK))
    #                 self.fc_combobox.append(gtk.combo_box_new_text())
    #                 self.fc_op_combobox.append(gtk.combo_box_new_text())
    #                 self.fc_op_combobox[i].append_text("=")
    #                 self.fc_op_combobox[i].append_text("<")
    #                 self.fc_op_combobox[i].append_text(">")
    #                 self.fc_op_combobox[i].append_text("!=")
    #                 self.fc_op_combobox[i].append_text("LIKE")
    #                 self.fc_op_combobox[i].append_text("NOT LIKE")
    #                 self.fc_op_combobox[i].append_text("ISNULL")
    #                 self.fc_op_combobox[i].append_text("NOT ISNULL")
    #                 if i:
    #                     self.fc_logic_combobox.append(gtk.combo_box_new_text())
    #                     self.fc_logic_combobox[i - 1].append_text("disabled")
    #                     self.fc_logic_combobox[i - 1].append_text("AND")
    #                     self.fc_logic_combobox[i - 1].append_text("OR")
    #                     table.attach(self.fc_logic_combobox[i - 1], 0, 1, i + 1, i + 2)
    #                     self.fc_logic_combobox[i - 1].show()
    #                 table.attach(self.fc_combobox[i], 1, 2, i + 1, i + 2)
    #                 table.attach(self.fc_op_combobox[i], 2, 3, i + 1, i + 2)
    #                 table.attach(self.fc_entry[i], 3, 4, i + 1, i + 2)
    #                 self.fc_combobox[i].show()
    #                 self.fc_op_combobox[i].show()
    #                 self.fc_entry[i].show()
    #         if not current_table:
    #             dialogs.show_message(
    #                 "info",
    #                 "no table selected!\nyou can't execute a template with "
    #                 "$field_conditions$ in it, if you have no table selected!")
    #             return
    #
    #         last_field = []
    #         for i in range(self.fc_count):
    #             last_field.append(self.fc_combobox[i].get_active_text())
    #             self.fc_combobox[i].get_model().clear()
    #             if i:
    #                 self.fc_logic_combobox[i - 1].set_active(0)
    #         fc = 0
    #         for field_name in current_table.field_order:
    #             for k in range(self.fc_count):
    #                 self.fc_combobox[k].append_text(field_name)
    #                 if last_field[k] == field_name:
    #                     self.fc_combobox[k].set_active(fc)
    #             fc += 1
    #         if not self.fc_op_combobox[0].get_active_text():
    #             self.fc_op_combobox[0].set_active(0)
    #         if not self.fc_combobox[0].get_active_text():
    #             self.fc_combobox[0].set_active(0)
    #
    #         answer = self.fc_window.run()
    #         self.fc_window.hide()
    #         if answer != gtk.RESPONSE_OK:
    #             return
    #
    #         def field_operator_value(field, op, value):
    #             if op == "ISNULL":
    #                 return "isnull(`%s`)" % field
    #             if op == "NOT ISNULL":
    #                 return "not isnull(`%s`)" % field
    #             eval_kw = "eval: "
    #             if value.startswith(eval_kw):
    #                 return "`%s` %s %s" % (field, op, value[len(eval_kw):])
    #             return "%s %s '%s'" % (self.current_host.escape_field(field), op, self.current_host.escape(value))
    #
    #         conditions = "%s" % (
    #             field_operator_value(
    #                 self.fc_combobox[0].get_active_text(),
    #                 self.fc_op_combobox[0].get_active_text(),
    #                 self.fc_entry[0].get_text()
    #             )
    #         )
    #         for i in range(1, self.fc_count):
    #             if self.fc_logic_combobox[i - 1].get_active_text() == "disabled" \
    #                     or self.fc_combobox[i].get_active_text() == "" \
    #                     or self.fc_op_combobox[i].get_active_text() == "":
    #                 continue
    #             conditions += " %s %s" % (
    #                 self.fc_logic_combobox[i - 1].get_active_text(),
    #                 field_operator_value(
    #                     self.fc_combobox[i].get_active_text(),
    #                     self.fc_op_combobox[i].get_active_text(),
    #                     self.fc_entry[i].get_text()
    #                 )
    #             )
    #         t = t.replace("$field_conditions$", conditions)
    #
    #     try:
    #         new_order = self.stored_orders[self.current_host.current_db.name][current_table.name]
    #         print "found stored order: %r" % (new_order, )
    #         query = t
    #         try:
    #             r = self.query_order_re
    #         except:
    #             r = self.query_order_re = re.compile(re_src_query_order)
    #         match = re.search(r, query)
    #         if match:
    #             before, order, after = match.groups()
    #             order = ""
    #             addition = ""
    #         else:
    #             match = re.search(re_src_after_order, query)
    #             if not match:
    #                 before = query
    #                 after = ""
    #             else:
    #                 before = query[0:match.start()]
    #                 after = match.group()
    #             addition = "\norder by\n\t"
    #         order = ""
    #         for col, o in new_order:
    #             if order:
    #                 order += ",\n\t"
    #             order += self.current_host.escape_field(col)
    #             if not o:
    #                 order += " desc"
    #         if order:
    #             new_query = ''.join([before, addition, order, after])
    #         else:
    #             new_query = re.sub("(?i)order[ \r\n\t]+by[ \r\n\t]+", "", before + after)
    #
    #         t = new_query
    #     except:
    #         pass
    #     self.events.trigger('execute_query')

    # def get_selected_table(self):
    #     path, column = self.connections_tv.get_cursor()
    #     depth = len(path)
    #     _iter = self.connections_tv.connections_model.get_iter(path)
    #     if depth == 3:
    #         return self.connections_tv.connections_model.get_value(_iter, 0)
    #     return None

    def process_events(self):
        """
        Process GTK events
        """
        while gtk.events_pending():
            gtk.main_iteration(False)
