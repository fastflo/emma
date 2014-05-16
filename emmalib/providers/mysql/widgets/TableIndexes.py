import gtk
import gobject


class TableIndexes(gtk.ScrolledWindow):

    def __init__(self, table):
        super(TableIndexes, self).__init__()

        self.table = table

        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.tv_indexes_model = gtk.ListStore(
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
        )
        self.tv_indexes = gtk.TreeView()
        self.tv_indexes.set_rules_hint(True)
        self.tv_indexes.set_model(self.tv_indexes_model)
        self.add(self.tv_indexes)

    def refresh(self):
        self.tv_indexes.append_column(gtk.TreeViewColumn("Name", gtk.CellRendererText(), text=0))
        self.tv_indexes.append_column(gtk.TreeViewColumn("Column", gtk.CellRendererText(), text=1))
        self.tv_indexes.append_column(gtk.TreeViewColumn("Unique", gtk.CellRendererText(), text=2))
        for ix in self.table.indexes:
            self.tv_indexes_model.append(
                (
                    ix.name,
                    ix.column,
                    ix.is_unique,
                )
            )
