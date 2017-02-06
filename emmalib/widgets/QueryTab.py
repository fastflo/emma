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

import gobject
import gtk
import gtksourceview2
import os
import re
import time
import traceback
from gtk import keysyms

import pango

from emmalib import Query
from emmalib import dialogs
from emmalib.Constants import icons_path

from emmalib.widgets import BaseTab
from querytab.QueryTabResultPopup import QueryTabResultPopup
from querytab.QueryTabTreeView import QueryTabTreeView
from emmalib.widgets.querytab.DatabaseEventBox import DatabaseEventBox
from emmalib.widgets.querytab.EncodingEventBox import EncodingEventBox
from emmalib.widgets.querytab.ResultToolbar import ResultToolbar
from emmalib.widgets.querytab.querytoolbar.QueryToolbar import QueryToolbar


class QueryTab(BaseTab):
    """
    @param emma: Emma
    """

    def __init__(self, emma):
        super(QueryTab, self).__init__()

        self.tab_label.set_text('Query')
        self.tab_label_icon.set_from_file(os.path.join(icons_path, 'page_code.png'))

        self.emma = emma

        self.ui = gtk.VPaned()

        # ---------------------------
        #   INIT TOP PART
        #

        vbox2 = gtk.VBox()

        self.query_toolbar = QueryToolbar(self, emma)
        vbox2.pack_start(self.query_toolbar, False, False)

        self.query_text_sw = gtk.ScrolledWindow()
        self.query_text_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.textview = gtk.TextView()
        self.query_text_sw.add(self.textview)

        vbox2.pack_end(self.query_text_sw, True, True)

        #
        #   INIT TOP PART
        # ---------------------------

        # ---------------------------
        #   INIT BOTTOM PART
        #

        hbox7 = gtk.HBox()
        self.toolbar = ResultToolbar(self, self.emma)
        hbox7.pack_start(self.toolbar, False, False)
        vbox3 = gtk.VBox()
        self.label = gtk.Label()
        self.label.set_alignment(0, 1)
        vbox3.pack_start(self.label, False, False)
        scrolledwindow6 = gtk.ScrolledWindow()
        scrolledwindow6.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.treeview = QueryTabTreeView(self.emma)
        scrolledwindow6.add(self.treeview)
        self.treeview.show()
        vbox3.pack_start(scrolledwindow6)
        hbox18 = gtk.HBox()
        self.encoding_event_box = EncodingEventBox(self, self.emma)
        self.database_event_box = DatabaseEventBox(self, self.emma)
        hbox18.add(self.encoding_event_box)
        hbox18.add(self.database_event_box)
        hbox18.show_all()
        vbox3.pack_end(hbox18, False, False)
        vbox3.show_all()
        hbox7.pack_end(vbox3, True, True)

        #
        #   INIT BOTTOM PART
        # ---------------------------

        self.ui.pack1(vbox2)
        self.ui.pack2(hbox7)
        self.ui.show_all()

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

        self.init_gtk_sourceview()

        self.current_host = None
        self.current_db = None
        self.model = None
        self.last_source = None
        self.result_info = None
        self.append_iter = None
        self.last_path = None
        self.encoding = None
        self.query_order_re = None
        self.kv_list = []
        self.last_th = None

        if hasattr(self, "query"):
            self.textview.get_buffer().set_text(self.query)
        self.last_auto_name = None

        self.init_from_config()

    def init_gtk_sourceview(self):
        """
        replace textview with gtksourcevice
        """
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

    def init_from_config(self):
        """
        Init from config file
        """
        self.set_query_encoding(self.emma.config.get("db_encoding"))
        self.set_query_font(self.emma.config.get("query_text_font"))
        self.set_result_font(self.emma.config.get("query_result_font"))
        if self.emma.config.get_bool("query_text_wrap"):
            self.set_wrap_mode(gtk.WRAP_WORD)
        else:
            self.set_wrap_mode(gtk.WRAP_NONE)
        self.set_current_host(self.emma.current_host)

    def on_query_view_cursor_changed(self, tv):
        """
        :param tv: gtk.TreeView
        :return: None
        """
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
            self.toolbar.apply_record.on_clicked(None)

    # todo: move to keymap
    def on_query_view_key_press_event(self, tv, event):
        """
        :param tv: gtk.TreeView
        :param event:
        :return:
        """
        path, column = self.treeview.get_cursor()
        if event.keyval == keysyms.F2:
            self.treeview.set_cursor(path, column, True)
            return True

        if not self.model:
            return False

        _iter = self.model.get_iter(path)
        if event.keyval == keysyms.Down and not self.model.iter_next(_iter):
            if self.append_iter and not self.toolbar.apply_record.on_apply_record_tool_clicked(
                    None):
                return True
            self.toolbar.add_record.on_add_record_tool_clicked(None)
            return True

    def on_query_view_button_press_event(self, tv, event):
        """
        :param tv: gtk.TreeView
        :param event:
        :return:
        """
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

    def auto_rename(self, new_auto_name):
        """
        :param new_auto_name: str
        :return: str
        """
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

    def destroy(self):
        """
        try to free some memory
        """
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
        """
        :param text: str
        """
        self.last_source = text
        self.textview.get_buffer().set_text(text)

    def update_db_label(self):
        """
        :return: None
        """
        h = self.current_host
        d = self.current_db
        if not h:
            self.database_event_box.set_label("no host/database selected")
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

        self.database_event_box.set_label("%s: %s@%s%s" % (
            title,
            h.user, hname,
            dname
        ))
        self.auto_rename("%s%s" % (h.name, dname))

    def set_current_host(self, host):
        """
        :param host:
        :return:
        """
        if self.current_host == host and host is not None and self.current_db == host.current_db:
            return
        self.current_host = host
        if host:
            self.current_db = host.current_db
        else:
            self.current_db = None
        self.update_db_label()

    def set_current_db(self, db):
        """
        :param db:
        """
        self.current_host = db.host
        self.current_db = db
        self.update_db_label()

    def set_query_encoding(self, encoding):
        """
        :param encoding: str
        """
        self.encoding = encoding
        self.encoding_event_box.set_label("encoding: %s" % self.encoding)

    def set_query_font(self, font_name):
        """
        :param font_name: str
        """
        self.textview.get_pango_context()
        fd = pango.FontDescription(font_name)
        self.textview.modify_font(fd)

    def set_result_font(self, font_name):
        """
        :param font_name: str
        """
        self.treeview.get_pango_context()
        fd = pango.FontDescription(font_name)
        self.treeview.modify_font(fd)

    def set_wrap_mode(self, wrap):
        """
        :param wrap: bool
        """
        self.textview.set_wrap_mode(wrap)

    def on_query_tab_label_close_button_clicked(self, button, page_index):
        """
        :param button: gtk.Button
        :param page_index: str
        """
        print button, page_index
        self.emma.main_notebook.close_query_tab(page_index)

    def is_query_editable(self, query, result=None):
        """
        :param query: str
        :param result:
        :return:
        """
        table, where, field, value, row_iter = self.get_unique_where(query)
        if not table or not where:
            return False
        return True

    def on_query_column_sort(self, column, col_num):
        """
        :param column:
        :param col_num: int
        """
        query = self.last_source
        current_order = Query.get_order_from_query(query)
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
            r = self.query_order_re = re.compile(Query.re_src_query_order)
        match = re.search(r, query)
        if match:
            before, order, after = match.groups()
            addition = ""
        else:
            match = re.search(Query.re_src_after_order, query)
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
            self.emma.events.trigger('execute_query')

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
        self.sort_timer_execute = time.time() + int(
            self.emma.config.get("result_view_column_sort_timeout")) / 1000.

    def get_unique_where(self, query, path=None, col_num=None, return_fields=False):
        # call is_query_appendable before!
        """
        :param query: str
        :param path:
        :param col_num: int
        :param return_fields: bool
        :return:
        """
        result = Query.is_query_appendable(query)
        if not result:
            return None, None, None, None, None

        field_list = result.group(6)
        table_list = result.group(7)

        # check tables
        table_list = table_list.replace(" join ", ",")
        table_list = re.sub(
            "(?i)(?:order[ \t\r\n]by.*|limit.*|group[ \r\n\t]by.*|order[ \r\n\t]by.*|where.*)",
            "", table_list)
        table_list = table_list.replace("`", "")
        tables = table_list.split(",")

        if len(tables) > 1:
            print "sorry, i can't edit queries with more than one source-table:", tables
            return None, None, None, None, None

        # get table_name
        table = tables[0].strip(" \r\n\t").strip("`'\"")
        # print "table:", table

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
        # print "fields:", fields

        wildcard = False
        for db_field_object in fields:
            if db_field_object.find("*") != -1:
                wildcard = True
                break

        # find table handle!
        th = None
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
                    print "query not editable, because table %r is not found in db %r" % \
                          (table, self.current_host.current_db)
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
        field_pos = 0
        for db_field_object in th.fields:
            has_mysql_primary = (pri_okay >= 0 and db_field_object.row['Key'] == "PRI")
            has_sqlite_id = (
                th.host.__class__.__name__ == "sqlite_host" and db_field_object.name.endswith("_id")
            )
            if has_mysql_primary or has_sqlite_id:
                if possible_primary:
                    possible_primary += ", "
                possible_primary += db_field_object.name
                if wildcard:
                    c = field_pos
                else:
                    c = None
                    try:
                        c = fields.index(db_field_object.name)
                    except:
                        pass
                if not c is None:
                    pri_okay = 1
                    if path:
                        value = self.model.get_value(row_iter, c)
                        if primary:
                            primary += " and "
                        primary += "`%s`='%s'" % (db_field_object.name, value)
                        self.kv_list.append((db_field_object.name, value))
            if uni_okay >= 0 and db_field_object.row['Key'] == "UNI":
                if possible_unique:
                    possible_unique += ", "
                possible_unique += db_field_object.name
                if wildcard:
                    c = field_pos
                else:
                    c = None
                    try:
                        c = fields.index(db_field_object.name)
                    except:
                        pass
                if not c is None:
                    uni_okay = 1
                    if path:
                        value = self.model.get_value(row_iter, c)
                        if unique:
                            unique += " and "
                        unique += "`%s`='%s'" % (db_field_object.name, value)
                        self.kv_list.append((db_field_object.name, value))
            field_pos += 1

        if uni_okay < 1 and pri_okay < 1:
            possible_key = "(i can't see any key-fields in this table...)"
            if possible_primary:
                possible_key = "e.g.'%s' would be useful!" % possible_primary
            elif possible_unique:
                possible_key = "e.g.'%s' would be useful!" % possible_unique
            print "no edit-key found. try to name a key-field in your select-clause. (%r)" % \
                  possible_key
            return table, None, None, None, None

        value = ""
        db_field_object = None

        where = ""

        # TODO: rework

        # if path:
        #     where = primary
        #     if not where:
        #         where = unique
        #     if not where:
        #         where = None
        #     if not col_num is None:
        #         value = self.model.get_value(row_iter, col_num)
        #         if wildcard:
        #             db_field_object = th.field_order[col_num]
        #         else:
        #             db_field_object = fields[col_num]
        # else:
        #     where = possible_primary + possible_unique

        # get current edited field and value by col_num
        if return_fields:
            return table, where, db_field_object, value, row_iter, fields
        return table, where, db_field_object, value, row_iter

    def on_query_change_data(self, cellrenderer, path, new_value, col_num, force_update=False):
        """
        :param cellrenderer:
        :param path:
        :param new_value:
        :param col_num:
        :param force_update:
        :return:
        """
        row_iter = self.model.get_iter(path)
        if self.append_iter \
                and self.model.iter_is_valid(self.append_iter) \
                and self.model.get_path(self.append_iter) == self.model.get_path(row_iter):
            self.filled_fields[self.treeview.get_column(col_num).get_title().replace("__", "_")] = \
                new_value
            self.model.set_value(row_iter, col_num, new_value)
            return

        table, where, field, value, row_iter = self.get_unique_where(
            self.last_source, path, col_num)
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
        """
        :return:
        """
        if not self.sort_timer_running:
            return False
        if self.sort_timer_execute > time.time():
            return True
        self.sort_timer_running = False
        self.emma.events.trigger('execute_query')
        return False

    def get_ui(self):
        """
        :return:
        """
        return self.ui
