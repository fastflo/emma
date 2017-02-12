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

import emmalib.dialogs
from emmalib.Query import *


class RememberOrder(gtk.ToolButton):
    def __init__(self, query, emma):
        """
        @param query: QueryTab
        @param emma: Emma
        """
        super(RememberOrder, self).__init__()
        self.emma = emma
        self.query = query

        self.set_label('Save Order')
        self.set_icon_name(gtk.STOCK_DIALOG_WARNING)
        self.set_tooltip_text('Remember order for this table!')

    def on_remember_order_clicked(self, _):
        query = self.query.last_source
        if not query:
            return None, None, None, None, None
        current_order = get_order_from_query(query)
        result = is_query_appendable(query)
        if not result:
            return None, None, None, None, None
        table_list = result.group(7)
        table_list = table_list.replace(" join ", ",")
        table_list = re.sub(
            "(?i)(?:order[ \t\r\n]by.*|limit.*|group[ \r\n\t]by.*|order[ \r\n\t]by.*|where.*)",
            "",
            table_list
        )
        table_list = table_list.replace("`", "")
        tables = map(lambda s: s.strip(), table_list.split(","))

        if len(tables) > 1:
            emmalib.dialogs.show_message(
                "store table order",
                "can't store table order of multi-table queries!"
            )
            return
        table = tables[0]

        # print "---\ntable: %s order: %s" % (table, current_order)

        config_name = "stored_order_db_%s_table_%s" % \
                      (self.emma.current_query.current_db.name, table)
        # print "config name %s" % config_name
        self.emma.config.config[config_name] = str(current_order)
        if self.emma.current_query.current_db.name not in self.emma.stored_orders:
            self.emma.stored_orders[self.emma.current_query.current_db.name] = {}
        self.emma.stored_orders[self.emma.current_query.current_db.name][table] = current_order
        self.emma.config.save()
