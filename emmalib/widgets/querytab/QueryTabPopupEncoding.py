"""
QueryTabPopupEncoding
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

import gtk


class QueryTabPopupEncoding(gtk.Menu):
    """
    @param query: QueryTab
    """

    def __init__(self, query):
        self.query = query

        super(QueryTabPopupEncoding, self).__init__()

        for key in self.query.emma.config.codings.keys():
            index, _ = self.query.emma.config.codings[key]
            item = gtk.MenuItem(key, False)
            item.connect("activate", self.on_query_encoding_changed, (key, index))
            self.append(item)
            item.show()

        self.show_all()

    def on_query_encoding_changed(self, _, data):
        """
        @param _:
        @param data:
        """
        self.query.set_query_encoding(data[0])
