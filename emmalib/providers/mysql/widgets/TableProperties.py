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

        self.properties = dict(zip(self.table.db.status_headers, self.table.props))

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

        hbox.pack_start(self.build_ltable(), False, False, 0)
        hbox.pack_start(self.build_rtable(), False, False, 16)
        vptp.add(hbox)
        vptp.set_shadow_type(gtk.SHADOW_NONE)
        self.add(vptp)
        self.show_all()

    def build_ltable(self):
        tbl = gtk.Table(4, 2)
        tbl.set_col_spacings(4)
        tbl.set_row_spacings(4)

        vbox = gtk.VBox()
        vbox_l = gtk.Label('Parameters')
        vbox_l.set_alignment(0, 1)
        vbox.pack_start(vbox_l, False, False)
        vbox.pack_start(gtk.HSeparator(), False, False, 4)
        vbox.pack_start(tbl, False, False, 4)

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
        self.btn_update.set_alignment(1, 0)
        tbl.attach(self.btn_update, 1, 2, r, r+1, 0, 0)

        return vbox

    def mklbl(self, text):
        lbl = gtk.Label(text+':')
        lbl.set_justify(gtk.JUSTIFY_RIGHT)
        lbl.set_alignment(1, 0)
        return lbl

    def build_rtable(self):
        itemlist = ['Update_time', 'Rows', 'Checksum', 'Check_time', 'Index_length', 'Data_length', 'Create_options',
                    'Avg_row_length', 'Data_free', 'Version', 'Create_time', 'Max_data_length']
        tbl = gtk.Table(len(itemlist), 2)
        tbl.set_col_spacings(4)
        tbl.set_row_spacings(4)

        vbox = gtk.VBox()
        vbox_l = gtk.Label('Properties')
        vbox_l.set_alignment(0, 1)
        vbox.pack_start(vbox_l, False, False)
        vbox.pack_start(gtk.HSeparator(), False, False, 4)
        vbox.pack_start(tbl, False, False, 4)

        r = 0
        for item in itemlist:
            e = gtk.Entry()
            e.set_editable(False)
            v = self.properties[item]
            if v is None:
                v = ''
            e.set_text(v)
            tbl.attach(self.mklbl(item), 0, 1, r, r+1, gtk.FILL, 0)
            tbl.attach(e, 1, 2, r, r+1, gtk.FILL, 0)
            r += 1

        return vbox

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
