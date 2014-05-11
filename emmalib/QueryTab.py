# -*- coding: utf-8 -*-
# emma
#
# Copyright (C) 2006 Florian Schmidt (flo@fastflo.de)
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

import gc
import gtk
import time
import pango
import gobject
import traceback
import gtksourceview2
from gtk import keysyms
from gtk import glade
from stat import *

import dialogs
import widgets
from QueryTabRememberOrder import QueryTabRememberOrder
from QueryTabRemoveOrder import QueryTabRemoveOrder
from QueryTabSetRequltFont import QueryTabSetResultFont
from QueryTabLocalSearch import QueryTabLocalSearch
from QueryTabSaveResultSql import QueryTabSaveResultSql
from QueryTabSaveResultCsv import QueryTabSaveResultCsv
from QueryTabManageRow import QueryTabManageRow
from QueryTabTreeView import QueryTabTreeView
from QueryTabResultPopup import QueryTabResultPopup
from QueryTabPopupEncoding import QueryTabPopupEncoding
from query_regular_expression import *
from Constants import *


class QueryTab(widgets.BaseTab):
    def __init__(self, emma):
        """
        @param emma: Emma
        """
        super(QueryTab, self).__init__()
        self.xml = gtk.glade.XML(os.path.join(emma.glade_path, 'querytab.glade'), "first_query")
        self.xml.signal_autoconnect(self)

        self.tab_label.set_text('Query')
        self.tab_label_icon.set_from_file(os.path.join(icons_path, 'page_code.png'))

        self.emma = emma

        self.save_result = self.xml.get_widget('save_result')
        self.save_result_sql = self.xml.get_widget('save_result_sql')
        self.local_search = self.xml.get_widget('local_search_button')
        self.remove_order = self.xml.get_widget('remove_order')

        self.label = self.xml.get_widget('query_label')

        self.add_record = self.xml.get_widget('add_record_tool')
        self.delete_record = self.xml.get_widget('delete_record_tool')

        self.query_bottom_label = self.xml.get_widget('query_bottom_label')
        self.query_db_label = self.xml.get_widget('query_db_label')

        self.textview = self.xml.get_widget('query_text')

        self.query_text_sw = self.xml.get_widget('query_text_sw')
        self.apply_record = self.xml.get_widget('apply_record_tool')
        self.ui = self.xml.get_widget('first_query')
        self.toolbar = self.xml.get_widget('inner_query_toolbar')
        self.toolbar.set_style(gtk.TOOLBAR_ICONS)

        self.scrolledwindow6 = self.xml.get_widget('scrolledwindow6')
        self.treeview = QueryTabTreeView(emma)
        self.scrolledwindow6.add(self.treeview)
        self.treeview.show()

        self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

        self.treeview.connect('cursor_changed', self.on_query_view_cursor_changed)
        # todo: move to keymap
        self.treeview.connect('key_press_event', self.on_query_view_key_press_event)
        self.treeview.connect('button_press_event', self.on_query_view_button_press_event)

        self.execution_timer_running = False
        self.execution_timer_interval = 0
        self.editable = False

        self.sort_timer_running = False
        self.sort_timer_execute = 0

        self.query_encoding_menu = None

        self.filled_fields = []

        # replace textview with gtksourcevice
        try:
            org_tv = self.textview
            manager = gtksourceview2.language_manager_get_default()
            language = manager.get_language("sql")

            sb = gtksourceview2.Buffer()
            sb.set_highlight_syntax(True)
            sb.set_language(language)
            sv = self.textview = gtksourceview2.View(sb)

            self.query_text_sw.remove(org_tv)
            self.query_text_sw.add(sv)
            sv.show()

            sv.set_show_line_numbers(True)
            sv.set_show_line_marks(True)
            sv.set_tab_width(4)
            sv.set_auto_indent(True)
            sv.set_insert_spaces_instead_of_tabs(False)
            sv.set_show_right_margin(True)
            sv.set_smart_home_end(True)
            sv.set_right_margin_position(80)

            # sv config
            # for pt, pn, pd in (
            #     (bool, "show_line_numbers", True),
            #     #(bool, "show_line_markers", False),
            #     #(int, "tabs_width", 4),
            #     (bool, "auto_indent", True),
            #     (bool, "insert_spaces_instead_of_tabs", False),
            #     #(bool, "show_margin", True),
            #     #(int, "margin", 80),
            #     (bool, "smart_home_end", True)
            # ):
            #
            #     cn = "sourceview.%s" % pn
            #     try:
            #         v = self.emma.config[cn]
            #         if pt == bool:
            #             v = v == "1" or v.lower() == "true" or v.lower() == "yes"
            #         else:
            #             v = pt(v)
            #     except:
            #         v = pd
            #     method = getattr(sv, "set_%s" % pn)
            #     method(v)
            # sb config
            # for pt, pn, pd in (
            #     (bool, "check_brackets", True),
            #     (bool, "highlight", True),
            #     (int, "max_undo_levels", 15)
            # ):
            #     cn = "sourceview.%s" % pn
            #     try:
            #         v = self.emma.config[cn]
            #         if pt == bool:
            #             v = v == "1" or v.lower() == "true" or v.lower() == "yes"
            #         else:
            #             v = pt(v)
            #     except:
            #         v = pd
            #     method = getattr(sb, "set_%s" % pn)
            #     method(v)
        except:
            dialogs.alert(traceback.format_exc())

        self.current_host = None
        self.current_db = None
        self.model = None
        self.last_source = None
        self.result_info = None
        self.append_iter = None
        self.last_path = None
        self.encoding = None
        if hasattr(self, "query"):
            self.textview.get_buffer().set_text(self.query)
        self.last_auto_name = None

        #
        #   INIT Query tab actions
        #

        self.remember_order_action = QueryTabRememberOrder(self, emma)
        self.remove_order_action = QueryTabRemoveOrder(self, emma)
        self.set_result_font_action = QueryTabSetResultFont(self, emma)
        self.local_search_action = QueryTabLocalSearch(self, emma)
        self.save_result_sql_action = QueryTabSaveResultSql(self, emma)
        self.save_result_csv_action = QueryTabSaveResultCsv(self, emma)
        self.manage_row_action = QueryTabManageRow(self, emma)

        #
        #
        #

        self.emma.key_map.connect('key-release', self.key_release)
        self.init_from_config()

    def init_from_config(self):
        self.set_query_encoding(self.emma.config.get("db_encoding"))
        self.set_query_font(self.emma.config.get("query_text_font"))
        self.set_result_font(self.emma.config.get("query_result_font"))
        if self.emma.config.get_bool("query_text_wrap"):
            self.set_wrap_mode(gtk.WRAP_WORD)
        else:
            self.set_wrap_mode(gtk.WRAP_NONE)
        self.set_current_host(self.emma.current_host)

    def key_release(self, key_map, event):
        pass

    def on_query_view_cursor_changed(self, tv):
        self.emma.blob_view.encoding = self.encoding
        path, column = self.treeview.get_cursor()

        if not path:
            return

        _iter = self.model.get_iter(path)
        if column is not None:
            col = self.treeview.get_columns().index(column)
        else:
            col = 0
        value = self.model.get_value(_iter, col)
        if value is None:
            # todo signal null value
            self.emma.blob_view.buffer.set_text("")
        else:
            self.emma.blob_view.buffer.set_text(value)
        self.emma.blob_view.tv.set_sensitive(True)

        if self.append_iter:
            if path == self.model.get_path(self.append_iter):
                return
            self.manage_row_action.on_apply_record_tool_clicked(None)

    # todo: move to keymap
    def on_query_view_key_press_event(self, tv, event):
        path, column = self.treeview.get_cursor()
        if event.keyval == keysyms.F2:
            self.treeview.set_cursor(path, column, True)
            return True

        if not self.model:
            return False

        _iter = self.model.get_iter(path)
        if event.keyval == keysyms.Down and not self.model.iter_next(_iter):
            if self.append_iter and not self.manage_row_action.on_apply_record_tool_clicked(None):
                return True
            self.manage_row_action.on_add_record_tool_clicked(None)
            return True

    def on_query_view_button_press_event(self, tv, event):
        selection = tv.get_selection()

        print selection.get_selected_rows()

        if event.button != 3 or selection.count_selected_rows() == 0:
            return False

        is_single_row = selection.count_selected_rows() == 1

        menu = QueryTabResultPopup(self, is_single_row)

        menu.popup(None, None, None, 0, 0)  # strange!
        #
        #   If selection is single row - let change row focus
        #
        if is_single_row:
            return False
        else:
            return True

    def on_query_bottom_eventbox_button_press_event(self, ebox, event):
        if not self.query_encoding_menu:
            self.query_encoding_menu = QueryTabPopupEncoding(self)
        self.query_encoding_menu.popup(None, None, None, event.button, event.time)

    def on_query_db_eventbox_button_press_event(self, ebox, event):
        q = self
        host = q.current_host
        db = q.current_db
        if q.last_path is not None:
            try:
                self.emma.connections_tv.connections_model.get_iter(q.last_path)
                self.emma.connections_tv.set_cursor(q.last_path)
                return
            except:
                # path was not valid
                pass

        i = self.emma.connections_tv.connections_model.get_iter_root()
        while i and self.emma.connections_tv.connections_model.iter_is_valid(i):
            if self.emma.connections_tv.connections_model[i][0] == host:
                break
            i = self.emma.connections_tv.connections_model.iter_next(i)
        else:
            print "host not found in connections list!"
            q.current_host = q.current_db = None
            q.update_db_label()
            return

        host_path = self.emma.connections_tv.connections_model.get_path(i)
        self.emma.connections_tv.scroll_to_cell(host_path, column=None, use_align=True, row_align=0.0, col_align=0.0)
        if db is None:
            self.emma.connections_tv.set_cursor(host_path)
            return
        k = self.emma.connections_tv.connections_model.iter_children(i)
        while k and self.emma.connections_tv.connections_model.iter_is_valid(k):
            if self.emma.connections_tv.connections_model[k][0] == db:
                break
            k = self.emma.connections_tv.connections_model.iter_next(k)
        else:
            print "database not found in connections list!"
            q.current_db = None
            q.update_db_label()
            self.emma.connections_tv.set_cursor(host_path)
            return
        path = self.emma.connections_tv.connections_model.get_path(k)
        #self.connections_tv.scroll_to_cell(path, column=None, use_align=True, row_align=0.125, col_align=0.0)
        self.emma.connections_tv.set_cursor(path)
        return

    def auto_rename(self, new_auto_name):
        label = self.get_label()
        if label is None:
            return
        if self.last_auto_name is None:
            print "no last_auto_name"
            label.set_text(new_auto_name)
            self.last_auto_name = new_auto_name
            return
        current_name = label.get_text()
        if self.last_auto_name in current_name:
            if current_name != new_auto_name:
                print "setting new %r from old %r" % (new_auto_name, current_name)
                label.set_text(current_name.replace(self.last_auto_name, new_auto_name))
                self.last_auto_name = new_auto_name
        else:
            print "last auto name %r not in %r!" % (self.last_auto_name, current_name)
        return

    def user_rename(self, new_name):
        # tab_widget = self.nb.get_tab_label(self.page)
        label = self.get_label()
        label.set_text(new_name)

    def destroy(self):
        # try to free some memory
        if self.model:
            self.model.clear()
        self.textview.get_buffer().set_text("")
        del self.treeview
        del self.model
        del self.textview
        self.treeview = None
        self.model = None
        self.textview = None
        self.update_db_label()

    def set(self, text):
        self.last_source = text
        self.textview.get_buffer().set_text(text)

    def update_db_label(self):
        h = self.current_host
        d = self.current_db
        if not h:
            self.query_db_label.set_label("no host/database selected")
            return
        title = "selected host"
        if d:
            dname = "/" + d.name
            title = "selected database"
        else:
            dname = ""
        if h.name == h.host:
            hname = h.name
        else:
            hname = "%s(%s)" % (h.name, h.host)

        self.query_db_label.set_label("%s: %s@%s%s" % (
            title,
            h.user, hname,
            dname
        ))
        self.auto_rename("%s%s" % (h.name, dname))

    def set_current_host(self, host):
        if self.current_host == host and host is not None and self.current_db == host.current_db:
            return
        self.current_host = host
        if host:
            self.current_db = host.current_db
        else:
            self.current_db = None
        self.update_db_label()

    def set_current_db(self, db):
        self.current_host = db.host
        self.current_db = db
        self.update_db_label()

    def update_bottom_label(self):
        self.query_bottom_label.set_label("encoding: %s" % self.encoding)

    def set_query_encoding(self, encoding):
        self.encoding = encoding
        self.update_bottom_label()

    def set_query_font(self, font_name):
        self.textview.get_pango_context()
        fd = pango.FontDescription(font_name)
        self.textview.modify_font(fd)

    def set_result_font(self, font_name):
        self.treeview.get_pango_context()
        fd = pango.FontDescription(font_name)
        self.treeview.modify_font(fd)

    def set_wrap_mode(self, wrap):
        self.textview.set_wrap_mode(wrap)

    def on_rename_query_tab_clicked(self, button):
        label = self.get_label()
        new_name = dialogs.input_dialog("Rename tab", "Please enter the new name of this tab:",
                                        label.get_text(),
                                        self.emma.mainwindow)
        if new_name is None:
            return
        if new_name == "":
            self.last_auto_name = None
            self.update_db_label()
            return
        self.user_rename(new_name)

    def on_closequery_button_clicked(self, button):
        self.emma.main_notebook.close_query_tab()

    def on_query_tab_label_close_button_clicked(self, button, page_index):
        print button, page_index
        self.emma.main_notebook.close_query_tab(page_index)

    def on_newquery_button_clicked(self, button):
        self.emma.main_notebook.add_query_tab()

    def on_query_font_clicked(self, button):
        d = self.emma.assign_once("query text font", gtk.FontSelectionDialog, "select query font")
        d.set_font_name(self.emma.config.get("query_text_font"))
        answer = d.run()
        d.hide()
        if not answer == gtk.RESPONSE_OK:
            return
        font_name = d.get_font_name()
        self.set_query_font(font_name)
        self.emma.config.config["query_text_font"] = font_name
        self.emma.config.save()

    def on_load_query_clicked(self, button):
        d = self.emma.assign_once(
            "load dialog",
            gtk.FileChooserDialog, "Load query", self.emma.mainwindow, gtk.FILE_CHOOSER_ACTION_OPEN,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))

        d.set_default_response(gtk.RESPONSE_ACCEPT)
        answer = d.run()
        d.hide()
        if not answer == gtk.RESPONSE_ACCEPT:
            return

        filename = d.get_filename()
        try:
            sbuf = os.stat(filename)
        except:
            dialogs.show_message("Load query", "%s does not exists!" % filename)
            return
        if not S_ISREG(sbuf.st_mode):
            dialogs.show_message("Load query", "%s exists, but is not a file!" % filename)
            return

        size = sbuf.st_size
        _max = int(self.emma.config.get("ask_execute_query_from_disk_min_size"))
        if size > _max:
            if dialogs.confirm("load query", """
<b>%s</b> is very big (<b>%.2fMB</b>)!
opening it in the normal query-view may need a very long time!
if you just want to execute this skript file without editing and
syntax-highlighting, i can open this file using the <b>execute file from disk</b> function.
<b>shall i do this?</b>""" % (filename, size / 1024.0 / 1000.0), self.emma.mainwindow):
                self.emma.on_execute_query_from_disk_activate(None, filename)
                return
        try:
            fp = file(filename, "rb")
            query_text = fp.read()
            fp.close()
        except:
            dialogs.show_message("Load Query", "Error reading query from file %s: %s" % (filename, sys.exc_value))
            return
        self.textview.get_buffer().set_text(query_text)

    def on_save_query_clicked(self, button):
        d = self.emma.assign_once(
            "save dialog",
            gtk.FileChooserDialog, "Save query", self.emma.mainwindow, gtk.FILE_CHOOSER_ACTION_SAVE,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))

        d.set_default_response(gtk.RESPONSE_ACCEPT)
        answer = d.run()
        d.hide()
        if not answer == gtk.RESPONSE_ACCEPT:
            return
        filename = d.get_filename()
        if os.path.exists(filename):
            if not os.path.isfile(filename):
                dialogs.show_message("save query", "%s already exists and is not a file!" % filename)
                return
            if not dialogs.confirm(
                    "Overwrite file?",
                    "%s already exists! Do you want to overwrite it?" % filename, self.emma.mainwindow):
                return
        b = self.textview.get_buffer()
        query_text = b.get_text(b.get_start_iter(), b.get_end_iter())
        try:
            fp = file(filename, "wb")
            fp.write(query_text)
            fp.close()
        except:
            dialogs.show_message("Save Query", "Error writing query to file %s: %s" % (filename, sys.exc_value))

    def on_execution_timeout(self, button):
        value = button.get_value()
        if value < 0.1:
            self.execution_timer_running = False
            return False
        if not self.on_execute_query_clicked():
            # stop on error
            button.set_value(0)
            value = 0
        if value != self.execution_timer_interval:
            self.execution_timer_running = False
            self.on_reexecution_spin_changed(button)
            return False
        return True

    def on_reexecution_spin_changed(self, button):
        value = button.get_value()
        if self.execution_timer_running:
            return
        self.execution_timer_running = True
        self.execution_timer_interval = value
        gobject.timeout_add(int(value * 1000), self.on_execution_timeout, button)

    def on_execute_query_clicked(self, button=None, query=None):
        field_count = 0
        if not query:
            b = self.textview.get_buffer()
            text = b.get_text(b.get_start_iter(), b.get_end_iter())
        else:
            text = query

        self.current_host = host = self.current_host
        if not host:
            dialogs.show_message(
                "error executing this query!",
                "could not execute query, because there is no selected host!"
            )
            return

        self.current_db = self.current_db
        if self.current_db:
            host.select_database(self.current_db)
        elif host.current_db:
            if not dialogs.confirm(
                    "query without selected db",
                    """warning: this query tab has no database selected
                    but the host-connection already has the database '%s' selected.
                    the author knows no way to deselect this database.
                    do you want to continue?""" % host.current_db.name, self.emma.mainwindow):
                return

        update = False
        select = False
        self.editable = False
        # single popup
        self.add_record.set_sensitive(False)
        self.delete_record.set_sensitive(False)
        # per query buttons
        self.add_record.set_sensitive(False)
        self.delete_record.set_sensitive(False)
        self.apply_record.set_sensitive(False)
        self.local_search.set_sensitive(False)
        self.remove_order.set_sensitive(False)
        self.save_result.set_sensitive(False)
        self.save_result_sql.set_sensitive(False)

        affected_rows = 0
        last_insert_id = 0
        num_rows = 0

        query_time = 0
        download_time = 0
        display_time = 0
        query_count = 0
        total_start = time.time()

        # cleanup last query model and treeview
        for col in self.treeview.get_columns():
            self.treeview.remove_column(col)
        if self.model:
            self.model.clear()

        _start = 0
        while _start < len(text):
            # search query end
            query_start, end = self.read_query(text, _start)
            if query_start is None:
                break
            thisquery = text[query_start:end]
            print "about to execute query %r" % thisquery
            _start = end + 1

            thisquery.strip(" \r\n\t;")
            if not thisquery:
                continue  # empty query
            query_count += 1
            query_hint = re.sub("[\n\r\t ]+", " ", thisquery[:40])
            self.label.set_text("executing query %d %s..." % (query_count, query_hint))
            self.label.window.process_updates(False)

            appendable = False
            appendable_result = self.is_query_appendable(thisquery)
            if appendable_result:
                appendable = True
                self.editable = self.is_query_editable(thisquery, appendable_result)
            print "appendable: %s, editable: %s" % (appendable, self.editable)

            ret = host.query(thisquery, encoding=self.encoding)
            query_time += host.query_time

            # if stop on error is enabled
            if not ret:
                print "mysql error: %r" % (host.last_error, )
                message = "error at: %s" % host.last_error.replace(
                    "You have an error in your SQL syntax.  "
                    "Check the manual that corresponds to your MySQL server version for the right syntax to use near ",
                    "")
                message = "error at: %s" % message.replace("You have an error in your SQL syntax; "
                                                           "check the manual that corresponds to your MySQL server "
                                                           "version for the right syntax to use near ", "")

                line_pos = 0
                pos = message.find("at line ")
                if pos != -1:
                    line_no = int(message[pos + 8:])
                    while 1:
                        line_no -= 1
                        if line_no < 1:
                            break
                        p = thisquery.find("\n", line_pos)
                        if p == -1:
                            break
                        line_pos = p + 1

                i = self.textview.get_buffer().get_iter_at_offset(query_start + line_pos)

                match = re.search("error at: '(.*)'", message, re.DOTALL)
                if match and match.group(1):
                    # set focus and cursor!
                    #print "search for ->%s<-" % match.group(1)
                    pos = text.find(match.group(1), query_start + line_pos, query_start + len(thisquery))
                    if not pos == -1:
                        i.set_offset(pos)
                else:
                    match = re.match("Unknown column '(.*?')", message)
                    if match:
                        # set focus and cursor!
                        pos = thisquery.find(match.group(1))
                        if not pos == 1:
                            i.set_offset(query_start + pos)

                self.textview.get_buffer().place_cursor(i)
                self.textview.scroll_to_iter(i, 0.0)
                self.textview.grab_focus()
                self.label.set_text(re.sub("[\r\n\t ]+", " ", message))
                return

            field_count = host.handle.field_count()
            if field_count == 0:
                # query without result
                update = True
                affected_rows += host.handle.affected_rows()
                last_insert_id = host.handle.insert_id()
                continue

            # query with result
            self.append_iter = None
            self.local_search.set_sensitive(True)
            self.add_record.set_sensitive(appendable)
            self.delete_record.set_sensitive(self.editable)
            select = True
            self.last_source = thisquery
            # get sort order!
            sortable = True  # todo
            current_order = self.get_order_from_query(thisquery)
            sens = False
            if len(current_order) > 0:
                sens = True
            self.remove_order.set_sensitive(sens and sortable)

            sort_fields = dict()
            for c, o in current_order:
                sort_fields[c.lower()] = o
            self.label.set_text("downloading resultset...")
            self.label.window.process_updates(False)

            start_download = time.time()
            result = host.handle.store_result()
            download_time = time.time() - start_download
            if download_time < 0:
                download_time = 0

            self.label.set_text("displaying resultset...")
            self.label.window.process_updates(False)

            # store field info
            self.result_info = result.describe()
            num_rows = result.num_rows()

            for col in self.treeview.get_columns():
                self.treeview.remove_column(col)

            columns = [gobject.TYPE_STRING] * field_count
            self.model = gtk.ListStore(*columns)
            self.treeview.set_model(self.model)
            self.treeview.set_rules_hint(True)
            self.treeview.set_headers_clickable(True)
            for i in range(field_count):
                title = self.result_info[i][0].replace("_", "__").replace("[\r\n\t ]+", " ")
                text_renderer = gtk.CellRendererText()
                if self.editable:
                    text_renderer.set_property("editable", True)
                    text_renderer.connect("edited", self.on_query_change_data, i)
                l = self.treeview.insert_column_with_data_func(
                    -1, title, text_renderer, widgets.ResultCellRenders.render_mysql_string, i)

                col = self.treeview.get_column(l - 1)

                if self.emma.config.get_bool("result_view_column_resizable"):
                    col.set_resizable(True)
                else:
                    col.set_resizable(False)
                    col.set_min_width(int(self.emma.config.get("result_view_column_width_min")))
                    col.set_max_width(int(self.emma.config.get("result_view_column_width_max")))

                if sortable:
                    col.set_clickable(True)
                    col.connect("clicked", self.on_query_column_sort, i)
                    # set sort indicator
                    field_name = self.result_info[i][0].lower()
                    try:
                        sort_col = sort_fields[field_name]
                        col.set_sort_indicator(True)
                        if sort_col:
                            col.set_sort_order(gtk.SORT_ASCENDING)
                        else:
                            col.set_sort_order(gtk.SORT_DESCENDING)
                    except:
                        col.set_sort_indicator(False)
                else:
                    col.set_clickable(False)
                    col.set_sort_indicator(False)

            cnt = 0
            start_display = time.time()
            last_display = start_display
            for row in result.fetch_row(0):
                def to_string(f):
                    if type(f) == str:
                        f = f.decode(self.encoding, "replace")
                    elif f is None:
                        pass
                    else:
                        f = str(f)
                    return f
                self.model.append(map(to_string, row))
                cnt += 1
                if not cnt % 100 == 0:
                    continue

                now = time.time()
                if (now - last_display) < 0.2:
                    continue

                self.label.set_text("displayed %d rows..." % cnt)
                self.label.window.process_updates(False)
                last_display = now

            display_time = time.time() - start_display
            if display_time < 0:
                display_time = 0

        result = []
        if select:
            # there was a query with a result
            result.append("rows: %d" % num_rows)
            result.append("fields: %d" % field_count)
            self.save_result.set_sensitive(True)
            self.save_result_sql.set_sensitive(True)
        if update:
            # there was a query without a result
            result.append("affected rows: %d" % affected_rows)
            result.append("insert_id: %d" % last_insert_id)
        total_time = time.time() - total_start
        result.append("| total time: %.2fs (query: %.2fs" % (total_time, query_time))
        if select:
            result.append("download: %.2fs display: %.2fs" % (download_time, display_time))
        result.append(")")

        self.label.set_text(' '.join(result))
        self.emma.blob_view.tv.set_editable(self.editable)
        self.emma.blob_view.blob_update.set_sensitive(self.editable)
        self.emma.blob_view.blob_load.set_sensitive(self.editable)
        # todo update_buttons()
        gc.collect()
        return True

    def is_query_editable(self, query, result=None):
        table, where, field, value, row_iter = self.get_unique_where(query)
        if not table or not where:
            return False
        return True

    def on_query_column_sort(self, column, col_num):
        query = self.last_source
        current_order = self.get_order_from_query(query)
        col = column.get_title().replace("__", "_")
        new_order = []
        for c, o in current_order:
            if c == col:
                if o:
                    new_order.append([col, False])
                col = None
            else:
                new_order.append([c, o])
        if col:
            new_order.append([self.current_host.escape_field(col), True])
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
        self.set(new_query)

        if self.emma.config.get("result_view_column_sort_timeout") <= 0:
            self.on_execute_query_clicked()

        new_order = dict(new_order)

        for col in self.treeview.get_columns():
            field_name = col.get_title().replace("__", "_")
            try:
                sort_col = new_order[field_name]
                col.set_sort_indicator(True)
                if sort_col:
                    col.set_sort_order(gtk.SORT_ASCENDING)
                else:
                    col.set_sort_order(gtk.SORT_DESCENDING)
            except:
                col.set_sort_indicator(False)

        if not self.sort_timer_running:
            self.sort_timer_running = True
            gobject.timeout_add(
                100 + int(self.emma.config.get("result_view_column_sort_timeout")),
                self.on_sort_timer
            )
        self.sort_timer_execute = time.time() + int(self.emma.config.get("result_view_column_sort_timeout")) / 1000.

    def is_query_appendable(self, query):
        pat = r'(?i)("(?:[^\\]|\\.)*?")|(\'(?:[^\\]|\\.)*?\')|(`(?:[^\\]|\\.)*?`)|(union)|(select[ \r\n\t]+(.*)[ \r\n\t]+from[ \r\n\t]+(.*))'
        if not self.current_host:
            return False
        try:
            r = self.query_select_re
        except:
            r = self.query_select_re = re.compile(pat)
        _start = 0
        result = False
        while 1:
            result = re.search(r, query[_start:])
            if not result:
                return False
            _start += result.end()
            if result.group(4):
                return False  # union
            if result.group(5) and result.group(6) and result.group(7):
                break  # found select
        return result

    def get_order_from_query(self, query, return_before_and_after=False):
        current_order = []
        try:
            r = self.query_order_re
        except:
            r = self.query_order_re = re.compile(re_src_query_order)
        # get current order by clause
        match = re.search(r, query)
        if not match:
            print "no order found in", [query]
            print "re:", [re_src_query_order]
            return current_order
        before, order, after = match.groups()
        order.lower()
        _start = 0
        ident = None
        while 1:
            item = []
            while 1:
                ident, end = self.read_expression(order[_start:])
                if not ident:
                    break
                if ident == ",":
                    break
                if ident[0] == "`":
                    ident = ident[1:-1]
                item.append(ident)
                _start += end
            l = len(item)
            if l == 0:
                break
            elif l == 1:
                item.append(True)
            elif l == 2:
                if item[1].lower() == "asc":
                    item[1] = True
                else:
                    item[1] = False
            else:
                print "unknown order item:", item, "ignoring..."
                item = None
            if item:
                current_order.append(tuple(item))
            if not ident:
                break
            _start += 1  # comma
        return current_order

    def get_unique_where(self, query, path=None, col_num=None, return_fields=False):
        # call is_query_appendable before!
        result = self.is_query_appendable(query)
        if not result:
            return None, None, None, None, None

        field_list = result.group(6)
        table_list = result.group(7)

        # check tables
        table_list = table_list.replace(" join ", ",")
        table_list = re.sub("(?i)(?:order[ \t\r\n]by.*|limit.*|group[ \r\n\t]by.*|order[ \r\n\t]by.*|where.*)",
                            "", table_list)
        table_list = table_list.replace("`", "")
        tables = table_list.split(",")

        if len(tables) > 1:
            print "sorry, i can't edit queries with more than one than one source-table:", tables
            return None, None, None, None, None

        # get table_name
        table = tables[0].strip(" \r\n\t").strip("`'\"")
        print "table:", table

        # check for valid fields
        field_list = re.sub("[\r\n\t ]+", " ", field_list)
        field_list = re.sub("'.*?'", "__BAD__STRINGLITERAL", field_list)
        field_list = re.sub("\".*?\"", "__BAD__STRINGLITERAL", field_list)
        field_list = re.sub("\\(.*?\\)", "__BAD__FUNCTIONARGUMENTS", field_list)
        field_list = re.sub("\\|", "__PIPE__", field_list)
        temp_fields = field_list.split(",")
        fields = []
        for f in temp_fields:
            fields.append(f.strip("` \r\n\t"))
        print "fields:", fields

        wildcard = False
        for field in fields:
            if field.find("*") != -1:
                wildcard = True
                break

        # find table handle!
        tries = 0
        new_tables = []
        self.last_th = None
        if not self.current_host:
            print "Host not selected"
            return None, None, None, None, None
        if not self.current_host.current_db:
            print "Database not selected"
            return None, None, None, None, None
        while 1:
            try:
                th = self.current_host.current_db.tables[table]
                break
            except:
                tries += 1
                if tries > 1:
                    print "query not editable, because table %r is not found in db %r" % (table,
                                                                                          self.current_host.current_db)
                    return None, None, None, None, None
                new_tables = self.current_host.current_db.refresh()
                continue
        # does this field really exist in this table?
        c = 0
        possible_primary = possible_unique = ""
        unique = primary = ""
        pri_okay = uni_okay = 0

        for i in new_tables:
            self.current_host.current_db.tables[i].refresh(False)

        if not th.fields and not table in new_tables:
            th.refresh(False)

        row_iter = None
        if path:
            row_iter = self.model.get_iter(path)

        # get unique where_clause
        self.kv_list = []
        self.last_th = th
        for field, field_pos in zip(th.field_order, range(len(th.field_order))):
            props = th.fields[field]
            if (
                (pri_okay >= 0 and props[3] == "PRI") or (
                    th.host.__class__.__name__ == "sqlite_host" and field.endswith("_id"))):
                if possible_primary:
                    possible_primary += ", "
                possible_primary += field
                if wildcard:
                    c = field_pos
                else:
                    c = None
                    try:
                        c = fields.index(field)
                    except:
                        pass
                if not c is None:
                    pri_okay = 1
                    if path:
                        value = self.model.get_value(row_iter, c)
                        if primary:
                            primary += " and "
                        primary += "`%s`='%s'" % (field, value)
                        self.kv_list.append((field, value))
            if uni_okay >= 0 and props[3] == "UNI":
                if possible_unique:
                    possible_unique += ", "
                possible_unique += field
                if wildcard:
                    c = field_pos
                else:
                    c = None
                    try:
                        c = fields.index(field)
                    except:
                        pass
                if not c is None:
                    uni_okay = 1
                    if path:
                        value = self.model.get_value(row_iter, c)
                        if unique:
                            unique += " and "
                        unique += "`%s`='%s'" % (field, value)
                        self.kv_list.append((field, value))

        if uni_okay < 1 and pri_okay < 1:
            possible_key = "(i can't see any key-fields in this table...)"
            if possible_primary:
                possible_key = "e.g.'%s' would be useful!" % possible_primary
            elif possible_unique:
                possible_key = "e.g.'%s' would be useful!" % possible_unique
            print "no edit-key found. try to name a key-field in your select-clause. (%r)" % possible_key
            return table, None, None, None, None

        value = ""
        field = None
        if path:
            where = primary
            if not where:
                where = unique
            if not where:
                where = None
            if not col_num is None:
                value = self.model.get_value(row_iter, col_num)
                if wildcard:
                    field = th.field_order[col_num]
                else:
                    field = fields[col_num]
        else:
            where = possible_primary + possible_unique

        # get current edited field and value by col_num
        if return_fields:
            return table, where, field, value, row_iter, fields
        return table, where, field, value, row_iter

    def read_expression(self, query, _start=0, concat=True, update_function=None, update_offset=0, icount=0):
        ## TODO!
        # r'(?is)("(?:[^\\]|\\.)*?")|(\'(?:[^\\]|\\.)*?\')|(`(?:[^\\]|\\.)*?`)|([^ \r\n\t]*[ \r\n\t]*\()|(\))|([0-9]+(?:\\.[0-9]*)?)|([^ \r\n\t,()"\'`]+)|(,)')
        try:
            r = self.query_expr_re
        except:
            r = self.query_expr_re = query_regular_expression

        # print "read expr in", query
        match = r.search(query, _start)
        #if match: print match.groups()
        if not match:
            return None, None
        for i in range(1, match.lastindex + 1):
            if match.group(i):
                t = match.group(i)
                e = match.end(i)
                current_token = t
                if current_token[len(current_token) - 1] == "(":
                    while 1:
                        icount += 1
                        if update_function is not None and icount >= 10:
                            icount = 0
                            update_function(False, update_offset + e)
                        #print "at", [query[e:e+15]], "..."
                        exp, end = self.read_expression(query, e, False, update_function, update_offset, icount)
                        #print "got inner exp:", [exp]
                        if not exp:
                            break
                        e = end
                        if concat:
                            t += " " + exp
                        if exp == ")":
                            break

                return t, e
        print "should not happen!"
        return None, None

    def on_query_change_data(self, cellrenderer, path, new_value, col_num, force_update=False):
        row_iter = self.model.get_iter(path)
        if self.append_iter \
                and self.model.iter_is_valid(self.append_iter) \
                and self.model.get_path(self.append_iter) == self.model.get_path(row_iter):
            self.filled_fields[self.treeview.get_column(col_num).get_title().replace("__", "_")] = new_value
            self.model.set_value(row_iter, col_num, new_value)
            return

        table, where, field, value, row_iter = self.get_unique_where(self.last_source, path, col_num)
        if force_update is False and new_value == value:
            return
        if self.current_host.__class__.__name__ == "sqlite_host":
            limit = ""
        else:
            limit = " limit 1"
        update_query = u"update %s set %s='%s' where %s%s" % (
            self.current_host.escape_table(table),
            self.current_host.escape_field(field),
            self.current_host.escape(new_value),
            where,
            limit
        )
        if self.current_host.query(update_query, encoding=self.encoding):
            print "set new value: %r" % new_value
            self.model.set_value(row_iter, col_num, new_value)
            return True
        return False

    def on_sort_timer(self):
        if not self.sort_timer_running:
            return False
        if self.sort_timer_execute > time.time():
            return True
        self.sort_timer_running = False
        self.on_execute_query_clicked()
        return False

    def read_query(self, query, _start=0):
        try:
            r = self.find_query_re
            rw = self.white_find_query_re
        except:
            r = self.find_query_re = re.compile(r"""
                (?s)
                (
                ("(?:[^\\]|\\.)*?")|            # double quoted strings
                ('(?:[^\\]|\\.)*?')|            # single quoted strings
                (`(?:[^\\]|\\.)*?`)|            # backtick quoted strings
                (/\*.*?\*/)|                    # c-style comments
                (\#[^\n]*)|                     # shell-style comments
                (\--[^\n]*)|                        # sql-style comments
                ([^;])                          # everything but a semicolon
                )+
            """, re.VERBOSE)
            rw = self.white_find_query_re = re.compile("[ \r\n\t]+")

        m = rw.match(query, _start)
        if m:
            _start = m.end(0)

        match = r.match(query, _start)
        if not match:
            return None, len(query)
        return match.start(0), match.end(0)

    def get_ui(self):
        return self.ui
