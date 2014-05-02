import gtk


class QueryTabResultPopup(gtk.Menu):
    def __init__(self, query, is_single_row):
        super(QueryTabResultPopup, self).__init__()

        self.query = query

        if is_single_row:
            self.copy_field_value = self.add_imi(
                gtk.STOCK_COPY,
                'copy_field_value',
                'Copy field value'
            )
            self.add_sep()

        self.copy_record_as_csv = self.add_imi(
            gtk.STOCK_COPY,
            'copy_record_as_csv',
            'Copy Record As CSV' if is_single_row else 'Copy Records As CSV'
        )
        self.copy_record_as_quoted_csv = self.add_imi(
            gtk.STOCK_COPY,
            'copy_record_as_quoted_csv',
            'Copy Record As Quoted CSV' if is_single_row else 'Copy Records As Quoted CSV'
        )
        self.add_sep()
        self.copy_column_as_csv = self.add_imi(
            gtk.STOCK_COPY,
            'copy_column_as_csv',
            'Copy Column As CSV'
        )
        self.copy_column_as_quoted_csv = self.add_imi(
            gtk.STOCK_COPY,
            'copy_column_as_quoted_csv',
            'Copy Column As Quoted CSV'
        )
        self.copy_column_names = self.add_imi(
            gtk.STOCK_COPY,
            'copy_column_names',
            'Copy Column Names'
        )
        #self.set_field_value = self.add_imi(gtk.STOCK_COPY, 'set_field_value', 'Set Field Value to...')
        self.add_sep()

        self.add_record = self.add_imi(
            gtk.STOCK_ADD,
            'add_record',
            'Add record'
        )
        self.delete_record = self.add_imi(
            gtk.STOCK_DELETE,
            'delete_record',
            'Delete record' if is_single_row else 'Delete records'
        )

        self.show_all()

    def add_sep(self):
        sep = gtk.SeparatorMenuItem()
        self.append(sep)

    def add_imi(self, stock, name, title):
        item = gtk.ImageMenuItem(stock)
        item.set_name(name)
        item.set_label(title)
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)
        return item

    def activated(self, item):
        q = self.query
        path, column = q.treeview.get_cursor()
        _iter = q.model.get_iter(path)

        if item.name == "copy_field_value":
            col_max = q.model.get_n_columns()
            for col_num in range(col_max):
                if column == q.treeview.get_column(col_num):
                    break
            else:
                print "column not found!"
                return
            value = q.model.get_value(_iter, col_num)
            self.query.set_text(value)
            self.query.emma.pri_clipboard.set_text(value)
        elif item.name == "copy_record_as_csv":
            col_max = q.model.get_n_columns()
            value = ""
            for col_num in range(col_max):
                if value:
                    value += self.query.emma.config.get("copy_record_as_csv_delim")
                v = q.model.get_value(_iter, col_num)
                if not v is None:
                    value += v
            self.query.emma.clipboard.set_text(value)
            self.query.emma.pri_clipboard.set_text(value)
        elif item.name == "copy_record_as_quoted_csv":
            col_max = q.model.get_n_columns()
            value = ""
            for col_num in range(col_max):
                if value:
                    value += self.query.emma.config.get("copy_record_as_csv_delim")
                v = q.model.get_value(_iter, col_num)
                if not v is None:
                    v = v.replace("\"", "\\\"")
                    value += '"%s"' % v
            self.query.emma.clipboard.set_text(value)
            self.query.emma.pri_clipboard.set_text(value)
        elif item.name == "copy_column_as_csv":
            col_max = q.model.get_n_columns()
            for col_num in range(col_max):
                if column == q.treeview.get_column(col_num):
                    break
            else:
                print "column not found!"
                return
            value = ""
            _iter = q.model.get_iter_first()
            while _iter:
                if value:
                    value += self.query.emma.config.get("copy_record_as_csv_delim")
                v = q.model.get_value(_iter, col_num)
                if not v is None:
                    value += v
                _iter = q.model.iter_next(_iter)
            self.query.emma.clipboard.set_text(value)
            self.query.emma.pri_clipboard.set_text(value)
        elif item.name == "copy_column_as_quoted_csv":
            col_max = q.model.get_n_columns()
            for col_num in range(col_max):
                if column == q.treeview.get_column(col_num):
                    break
            else:
                print "column not found!"
                return
            value = ""
            _iter = q.model.get_iter_first()
            while _iter:
                if value:
                    value += self.query.emma.config.get("copy_record_as_csv_delim")
                v = q.model.get_value(_iter, col_num)
                if not v is None:
                    v = v.replace("\"", "\\\"")
                    value += '"%s"' % v
                _iter = q.model.iter_next(_iter)
            self.query.emma.clipboard.set_text(value)
            self.query.emma.pri_clipboard.set_text(value)
        elif item.name == "copy_column_names":
            value = ""
            for col in q.treeview.get_columns():
                if value:
                    value += self.query.emma.config.get("copy_record_as_csv_delim")
                value += col.get_title().replace("__", "_")
            self.query.emma.clipboard.set_text(value)
            self.query.emma.pri_clipboard.set_text(value)
        elif item.name == "set_value_null":
            col_max = q.model.get_n_columns()
            for col_num in range(col_max):
                if column == q.treeview.get_column(col_num):
                    break
            else:
                print "column not found!"
                return
            table, where, field, value, row_iter = q.get_unique_where(q.last_source, path, col_num)
            update_query = "update `%s` set `%s`=NULL where %s limit 1" % (table, field, where)
            if self.query.query(update_query, encoding=q.encoding):
                q.model.set_value(row_iter, col_num, None)
        elif item.name == "set_value_now":
            col_max = q.model.get_n_columns()
            for col_num in range(col_max):
                if column == q.treeview.get_column(col_num):
                    break
            else:
                print "column not found!"
                return
            table, where, field, value, row_iter = q.get_unique_where(q.last_source, path, col_num)
            update_query = "update `%s` set `%s`=now() where %s limit 1" % (table, field, where)
            if not self.query.current_host.query(update_query, encoding=q.encoding):
                return
            self.query.current_host.query("select `%s` from `%s` where %s limit 1" % (field, table, where))
            result = self.query.current_host.handle.store_result().fetch_row(0)
            if len(result) < 1:
                print "error: can't find modfied row!?"
                return
            q.model.set_value(row_iter, col_num, result[0][0])
        elif item.name == "set_value_unix_timestamp":
            col_max = q.model.get_n_columns()
            for col_num in range(col_max):
                if column == q.treeview.get_column(col_num):
                    break
            else:
                print "column not found!"
                return
            table, where, field, value, row_iter = q.get_unique_where(q.last_source, path, col_num)
            update_query = "update `%s` set `%s`=unix_timestamp(now()) where %s limit 1" % (table, field, where)
            if not self.query.current_host.query(update_query, encoding=q.encoding):
                return
            self.query.current_host.query("select `%s` from `%s` where %s limit 1" % (field, table, where))
            result = self.query.current_host.handle.store_result().fetch_row(0)
            if len(result) < 1:
                print "error: can't find modfied row!?"
                return
            q.model.set_value(row_iter, col_num, result[0][0])
        elif item.name == "set_value_as_password":
            col_max = q.model.get_n_columns()
            for col_num in range(col_max):
                if column == q.treeview.get_column(col_num):
                    break
            else:
                print "column not found!"
                return
            table, where, field, value, row_iter = q.get_unique_where(q.last_source, path, col_num)
            update_query = "update `%s` set `%s`=password('%s') where %s limit 1" % (table, field,
                                                                                     self.query.current_host.escape(
                                                                                         value),
                                                                                     where)
            if not self.query.current_host.query(update_query, encoding=q.encoding):
                return
            self.query.current_host.query("select `%s` from `%s` where %s limit 1" % (field, table, where))
            result = self.query.current_host.handle.store_result().fetch_row(0)
            if len(result) < 1:
                print "error: can't find modfied row!?"
                return
            q.model.set_value(row_iter, col_num, result[0][0])
        elif item.name == "set_value_to_sha":
            col_max = q.model.get_n_columns()
            for col_num in range(col_max):
                if column == q.treeview.get_column(col_num):
                    break
            else:
                print "column not found!"
                return
            table, where, field, value, row_iter = q.get_unique_where(q.last_source, path, col_num)
            update_query = "update `%s` set `%s`=sha1('%s') where %s limit 1" % (table, field,
                                                                                 self.query.current_host.escape(value),
                                                                                 where)
            if not self.query.current_host.query(update_query, encoding=q.encoding):
                return
            self.query.current_host.query("select `%s` from `%s` where %s limit 1" % (field, table, where))
            result = self.query.current_host.handle.store_result().fetch_row(0)
            if len(result) < 1:
                print "error: can't find modfied row!?"
                return
            q.model.set_value(row_iter, col_num, result[0][0])