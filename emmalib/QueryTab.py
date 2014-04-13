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

import os
import pango
import gtk
import traceback
import gtksourceview2

from gtk import keysyms
from gtk import glade

from QueryTabRememberOrder import QueryTabRememberOrder
from QueryTabRemoveOrder import QueryTabRemoveOrder
from QueryTabSetRequltFont import QueryTabSetResultFont
from QueryTabLocalSearch import QueryTabLocalSearch
from QueryTabSaveResultSql import QueryTabSaveResultSql
from QueryTabSaveResultCsv import QueryTabSaveResultCsv
from QueryTabManageRow import QueryTabManageRow

from QueryTabTreeView import QueryTabTreeView


class QueryTab:
    def __init__(self, nb, emma):
        self.xml = gtk.glade.XML(os.path.join(emma.glade_path, 'querytab.glade'), "first_query")
        self.xml.signal_autoconnect(self)
        self.nb = nb
        self.emma = emma

        renameload = {
            "save_result": "save_result",
            "save_result_sql": "save_result_sql",
            "local_search": "local_search_button",
            "remove_order": "remove_order",
            "label": "query_label",
        }

        for attribute, xmlname in renameload.iteritems():
            self.__dict__[attribute] = self.xml.get_widget(xmlname)

        self.add_record = self.xml.get_widget('add_record_tool')
        self.delete_record = self.xml.get_widget('delete_record_tool')

        self.query_bottom_label = self.xml.get_widget('query_bottom_label')
        self.query_db_label = self.xml.get_widget('query_db_label')

        self.textview = self.xml.get_widget('query_text')

        self.query_text_sw = self.xml.get_widget('query_text_sw')
        self.apply_record = self.xml.get_widget('apply_record_tool')
        self.page = self.xml.get_widget('first_query')
        self.toolbar = self.xml.get_widget('inner_query_toolbar')
        self.toolbar.set_style(gtk.TOOLBAR_ICONS)

        self.scrolledwindow6 = self.xml.get_widget('scrolledwindow6')
        self.treeview = QueryTabTreeView(emma)
        self.scrolledwindow6.add(self.treeview)
        self.treeview.show()

        self.treeview.connect('cursor_changed', self.on_query_view_cursor_changed)
        self.treeview.connect('key_press_event', self.on_query_view_key_press_event)
        self.treeview.connect('button_release_event', self.on_query_view_button_release_event)

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
            from emmalib.dialogs import alert
            alert(traceback.format_exc())

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

    def __getstate__(self):
        b = self.textview.get_buffer()
        d = {
            "name": self.nb.get_tab_label_text(self.page),
            "query": b.get_text(b.get_start_iter(), b.get_end_iter())
        }
        print "query will pickle:", d
        return d

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

    def on_query_view_key_press_event(self, tv, event):
        path, column = self.treeview.get_cursor()
        if event.keyval == keysyms.F2:
            self.treeview.set_cursor(path, column, True)
            return True

        _iter = self.model.get_iter(path)
        if event.keyval == keysyms.Down and not self.model.iter_next(_iter):
            if self.append_iter and not self.manage_row_action.on_apply_record_tool_clicked(None):
                return True
            self.manage_row_action.on_add_record_tool_clicked(None)
            return True

    def on_query_view_button_release_event(self, tv, event):
        if not event.button == 3:
            return False
        res = tv.get_path_at_pos(int(event.x), int(event.y))
        menu = self.emma.xml.get_widget("result_popup")
        if res:
            sensitive = True
        else:
            sensitive = False
        for c in menu.get_children():
            for s in ["edit", "set ", "delete"]:
                if c.name.find(s) != -1:
                    c.set_sensitive(sensitive and self.emma.current_query.editable)
                    break
            else:
                if c.name not in ["add_record"]:
                    c.set_sensitive(sensitive)
                else:
                    c.set_sensitive(self.add_record.get_property("sensitive"))
        menu.popup(None, None, None, 0, event.time)  # strange!
        return True

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
            print "setting new %r from old %r" % (new_auto_name, current_name)
            label.set_text(current_name.replace(self.last_auto_name, new_auto_name))
            self.last_auto_name = new_auto_name
        else:
            print "last auto name %r not in %r!" % (self.last_auto_name, current_name)
        return

    def get_label(self):
        tab_widget = self.nb.get_tab_label(self.page)
        if not tab_widget:
            print "no tab widget"
            return
        labels = filter(lambda w: type(w) == gtk.Label, tab_widget.get_children())
        if not labels:
            print "no label found!"
            return
        return labels[0]

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
