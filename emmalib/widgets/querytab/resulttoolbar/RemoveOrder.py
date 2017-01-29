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
import re


class RemoveOrder(gtk.ToolButton):
    def __init__(self, query, emma):
        """
        @param query: QueryTab
        @param emma: Emma
        """
        self.emma = emma
        self.query = query
        super(RemoveOrder, self).__init__()

        self.set_label('Remove Order')
        self.set_icon_name(gtk.STOCK_CANCEL)
        self.set_tooltip_text('Remove order for this table')

        self.connect('clicked', self.on_remove_order_clicked)

    def on_remove_order_clicked(self, button):
        query = self.query.last_source
        try:
            r = self.emma.query_order_re
        except:
            r = self.emma.query_order_re = re.compile(self.emma.re_src_query_order)
        match = re.search(r, query)
        if not match:
            return
        before, order, after = match.groups()
        new_query = re.sub("(?i)order[ \r\n\t]+by[ \r\n\t]+", "", before + after)
        self.query.set(new_query)
        self.emma.sort_timer_running = False
        self.emma.events.emit('execute_query')

