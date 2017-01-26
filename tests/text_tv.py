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
import gobject
from emmalib.providers.mysql import MySqlHost
from emmalib.widgets.ResultCellRenders import render_mysql_string


class Win(gtk.Window):

    def __init__(self):
        super(Win, self).__init__()
        self.sw = gtk.ScrolledWindow()
        self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.add(self.sw)
        self.tv_data = gtk.TreeView()
        self.sw.add(self.tv_data)
        self.set_position(gtk.WIN_POS_CENTER)
        self.resize(640, 480)
        self.connect('destroy', lambda *args: gtk.main_quit())
        self.show_all()
        self.tv_data_model = None
        self.host = None
        self.table = None
        self.db_connect()
        self.load_data()

    def db_connect(self):
        _db = 'test'
        _tb = 'test'
        self.host = MySqlHost(None, None, 'Localhost', 'localhost', 3306, 'root', 'root', '', 0)
        self.host.connect()
        self.host.use_db(_db)
        self.host.databases[_db].refresh()
        self.host.databases[_db].tables[_tb].refresh()
        self.table = self.host.databases[_db].tables[_tb]

    def load_data(self):
        result = self.table.db.host.query_dict('SELECT * FROM %s' % self.table.name, append_to_log=False, encoding='utf8')
        if not result:
            return
        #
        #   Build list store with sort and data columns
        #   Make map of result column index, its display column and sort column
        #
        columns = []
        sort_display_map = []
        i = 0
        ci = 0
        for t in result['types']:
            columns.append(t)
            sort_index = i
            disp_index = sort_index
            i += 1
            if t == gobject.TYPE_LONG or t == gobject.TYPE_INT or t == gobject.TYPE_FLOAT:
                columns.append(gobject.TYPE_STRING)
                disp_index = i
                i += 1
            sort_display_map.append((ci, sort_index, disp_index))
            ci += 1

        print 'columns', columns
        print 'sort_display_map', sort_display_map

        #
        #   Add it all to model and in treeview
        #
        self.tv_data_model = gtk.ListStore(*columns)
        self.tv_data.set_model(self.tv_data_model)
        #
        #   Add treeview columns according to previously built index/sort/data map
        #
        for column_index, sort_index, disp_index in sort_display_map:
            title = result['cols'][column_index].replace("_", "__").replace("[\r\n\t ]+", " ")
            self.column_insert(title, sort_index, disp_index)

        for row in result['rows']:
            model_row = []
            for col in result['cols']:
                ci = result['cols'].index(col)
                if result['types'][ci] == gobject.TYPE_LONG:
                    if row[col] is None:
                        v = 0
                    else:
                        v = long(row[col])
                    model_row.append(v)
                    model_row.append(row[col])
                elif result['types'][ci] == gobject.TYPE_INT:
                    if row[col] is None:
                        v = 0
                    else:
                        v = int(row[col])
                    model_row.append(v)
                    model_row.append(row[col])
                elif result['types'][ci] == gobject.TYPE_FLOAT:
                    if row[col] is None:
                        v = 0
                    else:
                        v = float(row[col])
                    model_row.append(v)
                    model_row.append(row[col])
                elif result['types'][ci] == gobject.TYPE_STRING:
                    if row[col] is None:
                        model_row.append(None)
                    else:
                        try:
                            row[col].decode('ascii')
                            v = str(row[col])
                        except:
                            try:
                                v = row[col].decode('utf-8')
                            except UnicodeError:
                                v = '<BINARY>'
                        model_row.append(v)
            try:
                self.tv_data_model.append(model_row)
            except:
                pass
                #print "cannot add row:", model_row

    def column_insert(self, title, sort_column_index, display_column_index):
        text_renderer = gtk.CellRendererText()
        ci = self.tv_data.insert_column_with_data_func(
            -1,
            title,
            text_renderer,
            render_mysql_string,
            display_column_index)
        col = self.tv_data.get_column(ci-1)
        col.set_sort_column_id(sort_column_index)

w = Win()
gtk.main()