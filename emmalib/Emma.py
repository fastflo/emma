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
from dialogs.LocalSearch import LocalSearch


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
        self.key_map = None
        self.mainwindow = None
        self.current_query = None
        self.message_notebook = None
        self.main_notebook = None
        self.msg_log = None
        self.sql_log = None
        self.blob_view = None
        self.connections_tv = None
        #
        # init dialogs
        #
        self.about_dialog = dialogs.About()
        self.changelog_dialog = dialogs.ChangeLog()
        self.local_search_dialog = None
        #
        # init event manager
        #
        self.events = EventsManager()

    def start(self):
        """
        Start Emma process
        """

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

        self.local_search_dialog = LocalSearch(self)

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
                try:
                    _load(plugin_name)
                except Exception as e:
                    print "!!!could not load plugin %r" % plugin_name, e.message

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

    def process_events(self):
        """
        Process GTK events
        """
        while gtk.events_pending():
            gtk.main_iteration(False)
