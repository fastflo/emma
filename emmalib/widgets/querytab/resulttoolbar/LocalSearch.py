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

import re
import gtk

from emmalib import dialogs


class LocalSearch(gtk.ToolButton):

    def __init__(self, query, emma):
        """
        @param query: QueryTab
        @param emma: Emma
        """
        super(LocalSearch, self).__init__()
        self.emma = emma
        self.query = query

        self.set_label('Find')
        self.set_icon_name(gtk.STOCK_FIND)
        self.set_tooltip_text('Search for regular expression in this result (Ctrl+f / F3)')

        self.connect('clicked', self.on_local_search_button_clicked)

    def on_local_search_button_clicked(self, _, again=False):
        if not self.get_property("sensitive"):
            return
        self.emma.local_search_dialog.run(self.query, again)

