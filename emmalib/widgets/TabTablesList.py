import gtk
import gobject
from BaseTab import BaseTab


class TabTablesList(BaseTab):
    def __init__(self, emma):
        """
        @param emma: Emma
        """
        super(TabTablesList, self).__init__()

        self.tab_label.set_text('Tables List')
        self.ui = gtk.ScrolledWindow()
        self.ui.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.emma = emma
        self.model = None
        self.tables_db = None
        self.tables_count = 0
        self.tv = gtk.TreeView()
        self.ui.add(self.tv)
        self.ui.show_all()
        self.redraw()

    def redraw(self):
        if not self.emma.current_query:
            return
        elif self.emma.current_query.current_host:
            self.emma.current_host = self.emma.current_query.current_host
        else:
            return
        db = self.emma.current_host.current_db
        if not db:
            return

        if not self.tables_db == db:
            self.tables_db = db
            if self.model:
                self.model.clear()
                for col in self.tv.get_columns():
                    self.tv.remove_column(col)

            fields = db.status_headers
            columns = [gobject.TYPE_STRING] * len(fields)
            if not columns:
                return
            self.model = gtk.ListStore(*columns)
            self.tv.set_model(self.model)
            _id = 0
            for field in fields:
                title = field.replace("_", "__")
                self.tv.insert_column_with_data_func(
                    -1, title, gtk.CellRendererText(),
                    self.emma.render_mysql_string, _id)
                _id += 1
            self.tables_count = 0

        keys = db.tables.keys()
        if self.tables_count == len(keys):
            return
        self.tables_count = len(keys)
        keys.sort()
        if self.model:
            self.model.clear()
        for name in keys:
            table = db.tables[name]
            self.model.append(table.props)

    def get_ui(self):
        return self.ui
