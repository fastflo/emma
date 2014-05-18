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
from collations import collations


class TableProperties(gtk.ScrolledWindow):

    def __init__(self, table):
        super(TableProperties, self).__init__()
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.set_border_width(8)
        self.table = table

        self.tb_name = gtk.Entry()
        self.tb_ai = gtk.Entry()
        self.tb_comment = gtk.Entry()

        self.cb_engine = gtk.combo_box_new_text()
        self.cb_engine.append_text('InnoDB')
        self.cb_engine.append_text('MyISAM')

        self.cb_collation = gtk.combo_box_new_text()
        for c in collations:
            self.cb_collation.append_text(c)

        self.cb_rowformat = gtk.combo_box_new_text()
        self.cb_rowformat.append_text('Compact')
        self.cb_rowformat.append_text('Redundant')

        self.btn_update = gtk.Button('Update')

        vptp = gtk.Viewport()

        hbox = gtk.HBox()

        hbox.pack_start(self.build_ltable())
        hbox.pack_end(self.build_rtable())
        vptp.add(hbox)
        vptp.set_shadow_type(gtk.SHADOW_NONE)
        self.add(vptp)
        self.show_all()

        self.properties = dict(zip(self.table.db.status_headers, self.table.props))
        for p in self.properties:
            print p, self.properties[p]

    def build_ltable(self):
        tbl = gtk.Table(4, 2)

        r = 0
        tbl.attach(self.mklbl('Name'), 0, 1, r, r+1, gtk.FILL, 0)
        tbl.attach(self.tb_name, 1, 2, r, r+1, gtk.FILL, 0)

        r += 1
        tbl.attach(self.mklbl('Engine'), 0, 1, r, r+1, gtk.FILL, 0)
        tbl.attach(self.cb_engine, 1, 2, r, r+1, gtk.FILL, 0)

        r += 1
        tbl.attach(self.mklbl('Collation'), 0, 1, r, r+1, gtk.FILL, 0)
        tbl.attach(self.cb_collation, 1, 2, r, r+1, gtk.FILL, 0)

        r += 1
        tbl.attach(self.mklbl('Auto increment'), 0, 1, r, r+1, gtk.FILL, 0)
        tbl.attach(self.tb_ai, 1, 2, r, r+1, gtk.FILL, 0)

        r += 1
        tbl.attach(self.mklbl('Row format'), 0, 1, r, r+1, gtk.FILL, 0)
        tbl.attach(self.cb_rowformat, 1, 2, r, r+1, gtk.FILL, 0)

        r += 1
        tbl.attach(self.mklbl('Comment'), 0, 1, r, r+1, gtk.FILL, 0)
        tbl.attach(self.tb_comment, 1, 2, r, r+1, gtk.FILL, 0)

        r += 1
        tbl.attach(self.btn_update, 1, 2, r, r+1, gtk.FILL, 0)

        return tbl

    def mklbl(self, text):
        lbl = gtk.Label(text)
        lbl.set_justify(gtk.JUSTIFY_RIGHT)
        return lbl

    def build_rtable(self):
        r_table = gtk.Table(1, 2)
        r_table.attach(gtk.Label('aaa'), 0, 1, 0, 1, gtk.FILL, 0)
        r_table.attach(gtk.Label('bbb'), 1, 2, 0, 1, gtk.FILL, 0)
        return r_table

    def update(self):
        self.tb_name.set_text(self.properties['Name'])
        self.tb_ai.set_text(self.properties['Auto_increment'])
        self.tb_comment.set_text(self.properties['Comment'])

        self.selcb(self.cb_engine, self.properties['Engine'])
        self.selcb(self.cb_collation, self.properties['Collation'])
        self.selcb(self.cb_rowformat, self.properties['Row_format'])

    def selcb(self, cb, text):
        ix = 0
        for i in cb.get_model():
            if i[0] == text:
                cb.set_active(ix)
            ix += 1

    def update_old(self):
        table = self.table_properties
        prop_count = len(self.table.props)
        if len(self.table_property_labels) != prop_count:
            for c in self.table_property_labels:
                table.remove(c)
            for c in self.table_property_entries:
                table.remove(c)
            self.table_property_labels = []
            self.table_property_entries = []
            table.resize(prop_count, 2)
            r = 0
            for h, p in zip(self.table.db.status_headers, self.table.props):
                l = gtk.Label(h)
                l.set_alignment(0, 0.5)
                e = gtk.Entry()
                e.set_editable(False)
                if p is None:
                    p = ""
                e.set_text(p)
                table.attach(l, 0, 1, r, r + 1, gtk.FILL, 0)
                table.attach(e, 1, 2, r, r + 1, gtk.EXPAND | gtk.FILL | gtk.SHRINK, 0)
                l.show()
                e.show()
                self.table_property_labels.append(l)
                self.table_property_entries.append(e)
                r += 1
        else:
            r = 0
            for h, p in zip(self.table.db.status_headers, self.table.props):
                l = self.table_property_labels[r]
                e = self.table_property_entries[r]
                l.set_label(h)
                if p is None:
                    p = ""
                e.set_text(p)
                r += 1

