import gtk
import dialogs


class DeleteRecord(gtk.ToolButton):
    def __init__(self, query, emma):
        """
        @param query: QueryTab
        @param emma: Emma
        """
        super(DeleteRecord, self).__init__()
        self.emma = emma
        self.query = query

        self.set_label('Delete Record')
        self.set_icon_name(gtk.STOCK_DELETE)
        self.set_tooltip_text('Delete new record')

        self.connect('clicked', self.on_clicked)

    def on_clicked(self, button):
        q = self.query
        path, column = q.treeview.get_cursor()
        if not path:
            return
        row_iter = q.model.get_iter(path)
        if q.append_iter \
                and q.model.iter_is_valid(q.append_iter) \
                and q.model.get_path(q.append_iter) == q.model.get_path(row_iter):
            q.append_iter = None
            q.apply_record.set_sensitive(False)
        else:
            table, where, field, value, row_iter = self.query.get_unique_where(q.last_source, path)
            if not table or not where:
                dialogs.show_message("delete record", "could not delete this record!?")
                return
            if self.query.current_host.__class__.__name__ == "sqlite_host":
                limit = ""
            else:
                limit = " limit 1"
            update_query = "delete from `%s` where %s%s" % (table, where, limit)
            if not self.query.current_host.query(update_query, encoding=q.encoding):
                return
        if not q.model.remove(row_iter):
            row_iter = q.model.get_iter_first()
            while row_iter:
                new = q.model.iter_next(row_iter)
                if new is None:
                    break
                row_iter = new
        if row_iter:
            q.treeview.set_cursor(q.model.get_path(row_iter))
