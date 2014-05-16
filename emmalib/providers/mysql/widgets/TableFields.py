import gtk
import gobject
from TableFieldsPopUp import TableFieldsPopUp


class TableFields(gtk.ScrolledWindow):

    def __init__(self, table):
        super(TableFields, self).__init__()

        self.table = table

        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.tv_fields_model = gtk.ListStore(
            gobject.TYPE_BOOLEAN,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
        )
        self.tv_fields = gtk.TreeView()
        self.tv_fields.set_rules_hint(True)
        self.tv_fields.set_model(self.tv_fields_model)
        self.tv_fields.connect("button-release-event", self.on_button_release)
        self.pop_up = TableFieldsPopUp()
        self.add(self.tv_fields)

    def refresh(self):
        crt = gtk.CellRendererToggle()
        crt.connect('toggled', self.row_toggled, self.tv_fields_model)
        crt.set_activatable(True)
        tvc = gtk.TreeViewColumn("", crt)
        tvc.add_attribute(crt, "active", 0)
        self.tv_fields.append_column(tvc)
        self.tv_fields.append_column(gtk.TreeViewColumn("#", gtk.CellRendererText(), text=1))
        self.tv_fields.append_column(gtk.TreeViewColumn("Name", gtk.CellRendererText(), text=2))
        self.tv_fields.append_column(gtk.TreeViewColumn("Type", gtk.CellRendererText(), text=3))
        self.tv_fields.append_column(gtk.TreeViewColumn("Collation", gtk.CellRendererText(), text=4))
        self.tv_fields.append_column(gtk.TreeViewColumn("Null", gtk.CellRendererText(), text=5))
        self.tv_fields.append_column(gtk.TreeViewColumn("Default", gtk.CellRendererText(), text=6))
        self.tv_fields.append_column(gtk.TreeViewColumn("Extra", gtk.CellRendererText(), text=7))
        fn = 1
        for f in self.table.fields:
            self.tv_fields_model.append(
                (
                    False,
                    fn,
                    f.name,
                    f.type,
                    f.row['Collation'],
                    "YES" if f.is_null else "NO",
                    f.default,
                    f.row['Extra'],
                )
            )
            fn += 1

    def row_toggled(self, cell, path, model):
        if not cell or not path or not model:
            return
        model[path][0] = not model[path][0]

    def on_button_release(self, tv, event):
        if not tv or not event or not event.button == 3:
            return False
        self.pop_up.popup(None, None, None, event.button, event.time)
