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
import time
import gobject

from PopUpTabMsgLog import PopUpTabMsgLog


class TabMsgLog(gtk.ScrolledWindow):
    def __init__(self, emma):
        """
        @param emma: Emma
        """
        super(TabMsgLog, self).__init__()
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.emma = emma
        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.tv = gtk.TreeView()
        self.tv.set_model(self.model)
        self.tv.append_column(gtk.TreeViewColumn("Time", gtk.CellRendererText(), text=0))
        self.tv.append_column(gtk.TreeViewColumn("Message", gtk.CellRendererText(), text=1))

        self.tv.connect('button-press-event', self.on_msg_tv_button_press_event)

        self.menu = PopUpTabMsgLog()
        self.menu.connect('item-selected', self.menu_item_selected)

        self.add(self.tv)
        self.show_all()

    def log(self, log):
        if not log:
            return
        log.replace(
            "You have an error in your SQL syntax.  "
            "Check the manual that corresponds to your MySQL server version for the right syntax to use near",
            "syntax error at "
        )
        now = time.time()
        now = int((now - int(now)) * 100)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        if now:
            timestamp = "%s.%02d" % (timestamp, now)
        _iter = self.model.append((timestamp, log))
        self.tv.scroll_to_cell(self.model.get_path(_iter))
        self.emma.message_notebook.set_current_page(self.emma.message_notebook.page_num(self))

    def on_msg_tv_button_press_event(self, tv, event):
        if not event.button == 3:
            return False
        res = tv.get_path_at_pos(int(event.x), int(event.y))
        if not res:
            return False
        tv.set_cursor_on_cell(res[0])
        self.menu.popup(None, None, None, event.button, event.time)
        return True

    def menu_item_selected(self, menu, item):
        if item.name == "clear_messages":
            self.model.clear()
