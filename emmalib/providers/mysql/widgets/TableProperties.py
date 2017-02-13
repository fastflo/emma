"""
Emma MySql provider Table properties widget
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

from emmalib.dialogs import error
from emmalib.providers.mysql.widgets.collations import collations


class TableProperties(gtk.ScrolledWindow):
    """
    Emma MySql provider Table properties widget
    """
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
        self.cb_engine.connect('changed', self.on_cb_engine_changed)

        self.cb_charset = gtk.combo_box_new_text()
        self.cb_collation = gtk.combo_box_new_text()
        for c in collations:
            self.cb_charset.append_text(c)
        self.cb_charset.connect('changed', self.on_cb_charset_changed)

        self.cb_rowformat = gtk.combo_box_new_text()

        self.btn_update = gtk.Button('Update')
        self.btn_update.connect('clicked', self.on_update_clicked)

        vptp = gtk.Viewport()

        hbox = gtk.HBox()

        self.info_items_list = ['Update_time', 'Rows', 'Checksum', 'Check_time',
                                'Index_length', 'Data_length',
                                'Create_options', 'Avg_row_length', 'Data_free',
                                'Version', 'Create_time', 'Max_data_length']
        self.info_items_entries = {}

        hbox.pack_start(self.build_ltable(), False, False, 0)
        hbox.pack_start(self.build_rtable(), False, False, 16)
        vptp.add(hbox)
        vptp.set_shadow_type(gtk.SHADOW_NONE)
        self.add(vptp)
        self.show_all()

    def update(self):
        """
        Refresh table properties
        """
        for item in self.info_items_list:
            v = self.table.props_dict[item] if self.table.props_dict[item] is not None else ''
            self.info_items_entries[item].set_text(v)

        self.tb_name.set_text(self.table.props_dict['Name'])
        ai = self.table.props_dict.get('Auto_increment', '')
        self.tb_ai.set_text(ai if ai is not None else '')
        self.tb_comment.set_text(self.table.props_dict['Comment'])

        self.selcb(self.cb_engine, self.table.props_dict['Engine'])

        col = self.table.props_dict['Collation']
        col_s = col.split('_')
        if len(col_s) >= 2:
            self.selcb(self.cb_charset, col.split('_')[0])
        else:
            self.selcb(self.cb_charset, col)
        self.selcb(self.cb_collation, col)

        self.selcb(self.cb_rowformat, self.table.props_dict['Row_format'])

    def on_cb_charset_changed(self, cb):
        """
        Update table properties actions
        @param cb:
        """
        at = cb.get_active_text()
        self.cb_collation.get_model().clear()
        for i in collations[at]:
            self.cb_collation.append_text(i)
        self.selcb(self.cb_collation, at+'_general_ci')
        if self.cb_collation.get_active_text() is None:
            self.cb_collation.set_active(0)

    def on_update_clicked(self, *args):
        """
        @param args:
        @return:
        """
        if not args:
            return
        do_update = False
        if self.tb_name.get_text() != self.table.props_dict['Name']:
            if len(self.tb_name.get_text()) == 0:
                error('Table name cannot be empty')
            else:
                try:
                    if self.table.rename(self.tb_name.get_text()):
                        do_update = True
                except Exception as e:
                    error(e.message)
        if self.cb_engine.get_active_text() != self.table.props_dict['Engine']:
            if self.table.alter_engine(self.cb_engine.get_active_text()):
                do_update = True
        if self.cb_rowformat.get_active_text() != self.table.props_dict['Row_format']:
            if self.table.alter_row_format(self.cb_rowformat.get_active_text()):
                do_update = True
        if self.cb_collation.get_active_text() != self.table.props_dict['Collation']:
            if self.table.alter_collation(self.cb_charset.get_active_text(),
                                          self.cb_collation.get_active_text()):
                do_update = True
        if self.tb_comment.get_text() != self.table.props_dict['Comment']:
            if self.table.alter_comment(self.tb_comment.get_text()):
                do_update = True
        if self.tb_ai.get_text() != self.table.props_dict['Auto_increment']:
            if self.table.alter_auto_increment(self.tb_ai.get_text()):
                do_update = True
        if do_update:
            self.update()

    def on_cb_engine_changed(self, cmb):
        """
        @param cmb:
        """
        engine = cmb.get_active_text()
        self.cb_rowformat.get_model().clear()
        if engine == 'InnoDB':
            self.cb_rowformat.append_text('Compact')
            self.cb_rowformat.append_text('Compressed')
            self.cb_rowformat.append_text('Dynamic')
            self.cb_rowformat.append_text('Redundant')
            if self.table.props_dict['Engine'] == 'InnoDB':
                self.selcb(self.cb_rowformat, self.table.props_dict['Row_format'])
            else:
                self.selcb(self.cb_rowformat, 'Compact')
        elif engine == 'MyISAM':
            self.cb_rowformat.append_text('Fixed')
            self.cb_rowformat.append_text('Dynamic')
            if self.table.props_dict['Engine'] == 'MyISAM':
                self.selcb(self.cb_rowformat, self.table.props_dict['Row_format'])
            else:
                self.selcb(self.cb_rowformat, 'Dynamic')

    def build_ltable(self):
        """
        Build UI
        @return:
        """
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
        self.mkrow(tbl, self.tb_name, 'Name', r)
        r += 1
        self.mkrow(tbl, self.cb_engine, 'Engine', r)
        r += 1
        self.mkrow(tbl, self.cb_charset, 'Charset', r)
        r += 1
        self.mkrow(tbl, self.cb_collation, 'Collation', r)
        r += 1
        self.mkrow(tbl, self.tb_ai, 'Auto increment', r)
        r += 1
        self.mkrow(tbl, self.cb_rowformat, 'Row format', r)
        r += 1
        self.mkrow(tbl, self.tb_comment, 'Comment', r)
        r += 1
        self.btn_update.set_alignment(1, 0)
        tbl.attach(self.btn_update, 1, 2, r, r+1, 0, 0)

        return vbox

    def mkrow(self, tbl, child, label, r):
        """
        @param tbl:
        @param child:
        @param label:
        @param r:
        """
        tbl.attach(self.mklbl(label), 0, 1, r, r+1, gtk.FILL, 0)
        tbl.attach(child, 1, 2, r, r+1, gtk.FILL, 0)

    @staticmethod
    def mklbl(text):
        """
        @param text:
        @return:
        """
        lbl = gtk.Label(text+':')
        lbl.set_justify(gtk.JUSTIFY_RIGHT)
        lbl.set_alignment(1, 0)
        return lbl

    def build_rtable(self):
        """
        @return:
        """
        tbl = gtk.Table(len(self.info_items_list), 2)
        tbl.set_col_spacings(4)
        tbl.set_row_spacings(4)

        vbox = gtk.VBox()
        vbox_l = gtk.Label('Properties')
        vbox_l.set_alignment(0, 1)
        vbox.pack_start(vbox_l, False, False)
        vbox.pack_start(gtk.HSeparator(), False, False, 4)
        vbox.pack_start(tbl, False, False, 4)

        r = 0
        for item in self.info_items_list:
            e = gtk.Entry()
            e.set_editable(False)
            self.info_items_entries[item] = e
            v = self.table.props_dict.get(item, '')
            if v is None:
                v = ''
            e.set_text(v)
            tbl.attach(self.mklbl(item), 0, 1, r, r+1, gtk.FILL, 0)
            tbl.attach(e, 1, 2, r, r+1, gtk.FILL, 0)
            r += 1

        return vbox

    @staticmethod
    def selcb(cb, text):
        """
        @param cb:
        @param text:
        """
        ix = 0
        for i in cb.get_model():
            if i[0] == text:
                cb.set_active(ix)
            ix += 1
