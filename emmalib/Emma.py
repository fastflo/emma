import sql
import gtk
import glib
import gobject
import gtk.gdk
import dialogs
import widgets
import gtk.glade

from Config import Config
from KeyMap import KeyMap
from Constants import *
from query_regular_expression import *
from ConnectionTreeView import ConnectionsTreeView


class Emma:
    def __init__(self):
        self.emma_path = emma_path
        self.sql = sql
        self.created_once = {}
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
        self.xml.signal_autoconnect(self)

        self.key_map = KeyMap(self)

        self.mainwindow = widgets.MainWindow(self)
        self.mainwindow.connect('destroy', lambda *args: gtk.main_quit())

        self.mainwindow.connect('key_release_event', self.key_map.on_mainwindow_key_release_event)
        self.mainwindow.connect('key_press_event', self.key_map.on_mainwindow_key_press_event)

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

        self.plugin_pathes = []
        self.plugins = {}

        self.hosts = {}
        self.queries = []

        self.config = Config(self)
        self.config.load()

        self.connections_tv = ConnectionsTreeView(self)
        self.mainwindow.connections_tv_container.add(self.connections_tv)
        self.connections_tv.show()

        self.main_notebook.add_query_tab()

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

    def get_current_table(self):
        path, column = self.connections_tv.get_cursor()
        _iter = self.connections_tv.connections_model.get_iter(path)
        return path, column, _iter, self.connections_tv.connections_model.get_value(_iter, 0)

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

