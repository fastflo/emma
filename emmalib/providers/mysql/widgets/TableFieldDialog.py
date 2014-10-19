import gtk
from emmalib import emma_instance
from emmalib.providers.mysql.MySqlField import MySqlField
from collations import collations

field_types_conf = {
    'TINYINT': {
        'size': True, 'precission': False,
        'null': True, 'sign': True,
        'ai': True, 'pk': True,
        'un': True, 'ft': False,
        'default': True, 'charset': False
    },
    'SMALLINT': {
        'size': True, 'precission': False,
        'null': True, 'sign': True,
        'ai': True, 'pk': True,
        'un': True, 'ft': False,
        'default': True, 'charset': False
    },
    'MEDIUMINT': {
        'size': True, 'precission': False,
        'null': True, 'sign': True,
        'ai': True, 'pk': True,
        'un': True, 'ft': False,
        'default': True, 'charset': False
    },
    'INT': {
        'size': True, 'precission': False,
        'null': True, 'sign': True,
        'ai': True, 'pk': True,
        'un': True, 'ft': False,
        'default': True, 'charset': False
    },
    'BIGINT': {
        'size': True, 'precission': False,
        'null': True, 'sign': True,
        'ai': True, 'pk': True,
        'un': True, 'ft': False,
        'default': True, 'charset': False
    },
    'DECIMAL': {
        'size': True, 'precission': True,
        'null': True, 'sign': True,
        'ai': True, 'pk': True,
        'un': True, 'ft': False,
        'default': True, 'charset': False
    },
    'DOUBLE': {
        'size': True, 'precission': True,
        'null': True, 'sign': True,
        'ai': True, 'pk': True,
        'un': True, 'ft': False,
        'default': True, 'charset': False
    },
    'FLOAT': {
        'size': True, 'precission': True,
        'null': True, 'sign': True,
        'ai': True, 'pk': True,
        'un': True, 'ft': False,
        'default': True, 'charset': False
    },
    'REAL': {
        'size': True, 'precission': True,
        'null': True, 'sign': False,
        'ai': True, 'pk': True,
        'un': True, 'ft': False,
        'default': True, 'charset': False
    },
    'DATE': {
        'size': False, 'precission': False,
        'null': True, 'sign': False,
        'ai': False, 'pk': True,
        'un': True, 'ft': False,
        'default': True, 'charset': False
    },
    'DATETIME': {
        'size': False, 'precission': False,
        'null': True, 'sign': False,
        'ai': False, 'pk': True,
        'un': True, 'ft': False,
        'default': True, 'charset': False
    },
    'TIMESTAMP': {
        'size': False, 'precission': False,
        'null': True, 'sign': False,
        'ai': False, 'pk': True,
        'un': True, 'ft': False,
        'default': True, 'charset': False
    },
    'TIME': {
        'size': False, 'precission': False,
        'null': True, 'sign': False,
        'ai': False, 'pk': True,
        'un': True, 'ft': False,
        'default': True, 'charset': False
    },
    'YEAR': {
        'size': False, 'precission': False,
        'null': True, 'sign': False,
        'ai': False, 'pk': True,
        'un': True, 'ft': False,
        'default': True, 'charset': False
    },
    'CHAR': {
        'size': True, 'precission': False,
        'null': True, 'sign': False,
        'ai': False, 'pk': True,
        'un': True, 'ft': True,
        'default': True, 'charset': True
    },
    'VARCHAR': {
        'size': True, 'precission': False,
        'null': True, 'sign': False,
        'ai': False, 'pk': True,
        'un': True, 'ft': True,
        'default': True, 'charset': True
    },
    'BLOB': {
        'size': False, 'precission': False,
        'null': True, 'sign': False,
        'ai': False, 'pk': True,
        'un': True, 'ft': True,
        'default': True, 'charset': False
    },
    'TINYBLOB': {
        'size': False, 'precission': False,
        'null': True, 'sign': False,
        'ai': False, 'pk': True,
        'un': True, 'ft': True,
        'default': True, 'charset': False
    },
    'MEDIUMBLOB': {
        'size': False, 'precission': False,
        'null': True, 'sign': False,
        'ai': False, 'pk': True,
        'un': True, 'ft': True,
        'default': True, 'charset': False
    },
    'LONGBLOB': {
        'size': False, 'precission': False,
        'null': True, 'sign': False,
        'ai': False, 'pk': True,
        'un': True, 'ft': True,
        'default': True, 'charset': False
    },
    'TEXT': {
        'size': False, 'precission': False,
        'null': True, 'sign': False,
        'ai': False, 'pk': True,
        'un': True, 'ft': True,
        'default': True, 'charset': True
    },
    'TINYTEXT': {
        'size': False, 'precission': False,
        'null': True, 'sign': False,
        'ai': False, 'pk': True,
        'un': True, 'ft': True,
        'default': True, 'charset': True
    },
    'MEDIUMTEXT': {
        'size': False, 'precission': False,
        'null': True, 'sign': False,
        'ai': False, 'pk': True,
        'un': True, 'ft': True,
        'default': True, 'charset': True
    },
    'LONGTEXT': {
        'size': False, 'precission': False,
        'null': True, 'sign': False,
        'ai': False, 'pk': True,
        'un': True, 'ft': True,
        'default': True, 'charset': True
    },
    'BINARY': {
        'size': True, 'precission': False,
        'null': True, 'sign': False,
        'ai': False, 'pk': True,
        'un': True, 'ft': True,
        'default': True, 'charset': True
    },
    'VARBINARY': {
        'size': True, 'precission': False,
        'null': True, 'sign': False,
        'ai': False, 'pk': True,
        'un': True, 'ft': True,
        'default': True, 'charset': True
    },
    'ENUM': {
        'size': False, 'precission': False,
        'null': True, 'sign': False,
        'ai': False, 'pk': False,
        'un': False, 'ft': False,
        'default': True, 'charset': False
    },
    'SET': {
        'size': True, 'precission': False,
        'null': True, 'sign': False,
        'ai': False, 'pk': False,
        'un': False, 'ft': False,
        'default': True, 'charset': False
    }
}


class TableFieldDialog(gtk.Dialog):
    
    def __init__(self, field):

        self.field = field

        if field.name:
            super(TableFieldDialog, self).__init__(
                'Edit field: %s' % field.name,
                emma_instance.mainwindow if emma_instance else None,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_APPLY, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
            )
        else:
            super(TableFieldDialog, self).__init__(
                'Add Field',
                emma_instance.mainwindow if emma_instance else None,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_ADD, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
            )

        self.set_border_width(8)

        self.vbox.set_spacing(8)
        lbl = gtk.Label('Field properties')
        lbl.set_justify(gtk.JUSTIFY_LEFT)
        lbl.set_alignment(0, 0)
        self.vbox.pack_start(lbl)
        self.vbox.pack_start(gtk.HSeparator())

        self.tb_name = gtk.Entry()
        self.tb_name.set_text(field.name)
        self.cb_type = gtk.combo_box_new_text()
        for t in sorted(field_types_conf):
            self.cb_type.append_text(t)

        self.sp_size = gtk.SpinButton(gtk.Adjustment(11.0, 1.0, 1024.0, 1.0, 5.0, 0.0), 0, 0)
        self.sp_size.set_value(float(field.size))
        self.sp_size.set_wrap(True)

        self.sp_prec = gtk.SpinButton(gtk.Adjustment(0.0, 0.0, 16.0, 1.0, 5.0, 0.0), 0, 0)
        self.sp_prec.set_value(float(field.precission))
        self.sp_prec.set_wrap(True)

        self.cb_null = gtk.CheckButton()
        self.cb_null.set_active(field.is_null)

        self.cb_sign = gtk.CheckButton()
        self.cb_sign.set_active(field.unsigned)

        self.cb_auto_increment = gtk.CheckButton()
        self.cb_auto_increment.set_active(field.auto_increment)

        self.cb_primary = gtk.CheckButton()
        self.cb_unique = gtk.CheckButton()
        self.cb_fulltext = gtk.CheckButton()

        self.tb_default = gtk.Entry()

        self.cb_charset = gtk.combo_box_new_text()
        self.cb_collation = gtk.combo_box_new_text()
        for c in sorted(collations):
            self.cb_charset.append_text(c)
        self.cb_charset.connect('changed', self.on_cb_charset_changed)

        self.cb_type.connect('changed', self.on_cb_type_changed)
        self.selcb(self.cb_type, field.type.upper())

        tbl = gtk.Table(4, 4)
        tbl.set_col_spacings(8)
        tbl.set_row_spacings(8)

        r = 0
        tbl.attach(self.mklbl('Name'), 0, 1, r, r+1, gtk.FILL, 0)
        tbl.attach(self.tb_name, 1, 4, r, r+1, gtk.FILL, 0)
        r += 1
        self.mksep(tbl, r)
        r += 1
        tbl.attach(self.mklbl('Type'), 0, 1, r, r+1, gtk.FILL, 0)
        tbl.attach(self.cb_type, 1, 4, r, r+1, gtk.FILL, 0)
        r += 1
        self.mkrow(tbl, self.sp_size, 'Size', r)
        self.mkrow(tbl, self.sp_prec, 'Precission', r, 2)
        r += 1
        self.mksep(tbl, r)
        r += 1
        self.mkrow(tbl, self.cb_null, 'Is NULL', r)
        self.mkrow(tbl, self.cb_sign, 'Unsigned', r, 2)
        r += 1
        self.mksep(tbl, r)
        r += 1
        self.mkrow(tbl, self.cb_auto_increment, 'Auto Increment', r)
        self.mkrow(tbl, self.cb_primary, 'Primary key', r, 2)
        r += 1
        self.mkrow(tbl, self.cb_unique, 'Unique', r)
        self.mkrow(tbl, self.cb_fulltext, 'Fulltext', r, 2)
        r += 1
        self.mksep(tbl, r)
        r += 1
        tbl.attach(self.mklbl('Default'), 0, 1, r, r+1, gtk.FILL, 0)
        tbl.attach(self.tb_default, 1, 4, r, r+1, gtk.FILL, 0)
        r += 1
        self.mksep(tbl, r)
        r += 1
        tbl.attach(self.mklbl('Charset'), 0, 1, r, r+1, gtk.FILL, 0)
        tbl.attach(self.cb_charset, 1, 4, r, r+1, gtk.FILL, 0)
        r += 1
        tbl.attach(self.mklbl('Collation'), 0, 1, r, r+1, gtk.FILL, 0)
        tbl.attach(self.cb_collation, 1, 4, r, r+1, gtk.FILL, 0)
        r += 1
        self.mksep(tbl, r)

        self.vbox.pack_start(tbl)

        self.show_all()

    def on_cb_type_changed(self, cb):
        at = cb.get_active_text()
        conf = field_types_conf[at]
        self.sp_size.set_sensitive(conf['size'])
        self.sp_prec.set_sensitive(conf['precission'])
        self.cb_null.set_sensitive(conf['null'])
        self.cb_sign.set_sensitive(conf['sign'])

        self.cb_auto_increment.set_sensitive(conf['ai'])
        self.cb_primary.set_sensitive(conf['pk'])
        self.cb_unique.set_sensitive(conf['un'])
        self.cb_fulltext.set_sensitive(conf['ft'])

        self.tb_default.set_sensitive(conf['default'])
        self.cb_charset.set_sensitive(conf['charset'])

    def on_cb_charset_changed(self, cb):
        at = cb.get_active_text()
        self.cb_collation.get_model().clear()
        for i in sorted(collations[at]):
            self.cb_collation.append_text(i)
        self.selcb(self.cb_collation, at+'_general_ci')
        if self.cb_collation.get_active_text() is None:
            self.cb_collation.set_active(0)

    def mkrow(self, tbl, child, label, r, o=0):
        tbl.attach(self.mklbl(label), 0+o, 1+o, r, r+1, gtk.FILL, 0)
        tbl.attach(child, 1+o, 2+o, r, r+1, gtk.FILL, 0)

    def mksep(self, tbl, r):
        tbl.attach(gtk.HSeparator(), 0, 4, r, r+1, gtk.FILL, 0)

    def mklbl(self, text):
        lbl = gtk.Label(text+':')
        lbl.set_justify(gtk.JUSTIFY_RIGHT)
        lbl.set_alignment(1, 0)
        return lbl

    def selcb(self, cb, text):
        ix = 0
        for i in cb.get_model():
            if i[0] == text:
                cb.set_active(ix)
            ix += 1

    def get_sql(self, table_name):
        sql = ''
        if self.field.name == '':
            sql += 'ALTER TABLE `%s` ADD COLUMN `%s`' % (table_name, self.tb_name.get_text(),)
        else:
            sql += 'ALTER TABLE `%s` CHANGE `%s` `%s`' % (table_name, self.field.name, self.tb_name.get_text(),)

        sql += ' %s(%s)' % (self.cb_type.get_active_text(), int(self.sp_size.get_value()),)

        if self.cb_sign.get_active():
            sql += ' UNSIGNED '

        if self.cb_null.get_active():
            sql += ' NULL '
        else:
            sql += ' NOT NULL '

        if self.cb_auto_increment.get_active():
            sql += ' AUTO_INCREMENT '

        if self.tb_default.get_text() != '':
            sql += ' DEFAULT %s' % (self.tb_default.get_text())

        print sql

        return sql


if __name__ == '__main__':

    f = MySqlField({})
    w = TableFieldDialog(f)
    answer = w.run()
    if answer == gtk.RESPONSE_OK:
        print w.get_sql('table_name')
    w.destroy()