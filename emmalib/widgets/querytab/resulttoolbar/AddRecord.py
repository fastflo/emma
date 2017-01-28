import gtk


class AddRecord(gtk.ToolButton):
    def __init__(self, query, emma):
        """
        @param query: QueryTab
        @param emma: Emma
        """
        super(AddRecord, self).__init__()
        self.emma = emma
        self.query = query

        self.set_label('Add Record')
        self.set_icon_name(gtk.STOCK_ADD)
        self.set_tooltip_text('Add new record')

        self.connect('clicked', self.on_clicked)

    def on_clicked(self, button):
        q = self.query
        if not q.toolbar.add_record.get_property("sensitive"):
            return

        path, column = q.treeview.get_cursor()
        if path:
            _iter = q.model.insert_after(q.model.get_iter(path))
        else:
            _iter = q.model.append()
        q.treeview.grab_focus()
        q.treeview.set_cursor(q.model.get_path(_iter))
        q.filled_fields = dict()
        q.append_iter = _iter
        q.toolbar.apply_record.set_sensitive(True)
