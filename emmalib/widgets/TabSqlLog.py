"""
TabSqlLog
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

import time
import gobject
import gtk

from emmalib.widgets.PopUpTabSqlLog import PopUpTabSqlLog


class TabSqlLog(gtk.ScrolledWindow):
    """
    @param emma: Emma
    """

    def __init__(self, emma):
        super(TabSqlLog, self).__init__()
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.emma = emma
        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.tv = gtk.TreeView()
        self.tv.set_model(self.model)
        self.tv.append_column(gtk.TreeViewColumn("Time", gtk.CellRendererText(), text=0))
        self.tv.append_column(gtk.TreeViewColumn("Query", gtk.CellRendererText(), markup=1))

        self.tv.connect('row-activated', self.on_sql_log_activate)
        self.tv.connect('button-press-event', self.on_sql_log_button_press)

        self.menu = PopUpTabSqlLog()
        self.menu.connect('item-selected', self.menu_item_selected)

        self.add(self.tv)
        self.show_all()

    def log(self, log):
        """
        @param log:
        @return:
        """
        olog = log
        max_len = int(self.emma.config.get("query_log_max_entry_length"))
        if len(log) > max_len:
            log = log[0:max_len] + "\n/* query with length of %d bytes truncated. */" % len(log)

        if not log:
            return

        now = time.time()
        now = int((now - int(now)) * 100)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        if now:
            timestamp = "%s.%02d" % (timestamp, now)
        log = log.replace("<", "&lt;")
        log = log.replace(">", "&gt;")
        _iter = self.model.append((timestamp, log, olog))
        self.tv.scroll_to_cell(self.model.get_path(_iter))
        self.emma.message_notebook.set_current_page(self.emma.message_notebook.page_num(self))
        self.emma.process_events()

    def on_sql_log_activate(self, tv, path, tvc):
        """
        @type tvc: gtk.TreeViewColumn
        @type path: tuple
        @type tv: gtk.TreeVie
        @return: bool
        """
        if not tvc:
            return
        query = tv.get_model()[path][2]
        self.emma.current_query.textview.get_buffer().set_text(query)
        return True

    def on_sql_log_button_press(self, tv, event):
        """
        @type event: gtk.gdk.Event
        @type tv: gtk.TreeView
        @param tv:
        @param event:
        @return:
        """
        print "on_sql_log_button_press", tv, event
        if not event.button == 3:
            return False
        res = tv.get_path_at_pos(int(event.x), int(event.y))
        if not res:
            return False
        tv.set_cursor_on_cell(res[0])
        self.menu.popup(None, None, None, event.button, event.time)
        return True

    def menu_item_selected(self, menu, item):
        """
        @type menu: gtk.Menu
        @param menu: Element from PopUpTabSqlLog
        @param item:
        @return: bool
        """
        if not menu:
            return False
        if item.name == "clear_all_entries":
            self.model.clear()
            return True

        path, _ = self.tv.get_cursor()

        if not path:
            return False
        row = self.model[path]
        if item.name == "copy_sql_log":
            self.emma.clipboard.set_text(row[2])
            self.emma.pri_clipboard.set_text(row[2])
        elif item.name == "set_as_query_text":
            self.emma.current_query.textview.get_buffer().set_text(row[2])
        if item.name == "delete_sql_log":
            _iter = self.model.get_iter(path)
            self.model.remove(_iter)
        return True
