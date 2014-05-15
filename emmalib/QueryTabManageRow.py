import dialogs


class QueryTabManageRow:

    def __init__(self, query, emma):
        """
        @param query: QueryTab
        @param emma: Emma
        """
        self.emma = emma
        self.query = query

        button_add = self.query.xml.get_widget('add_record_tool')
        button_add.connect('clicked', self.on_add_record_tool_clicked)

        button_del = self.query.xml.get_widget('delete_record_tool')
        button_del.connect('clicked', self.on_delete_record_tool_clicked)

        button_apl = self.query.xml.get_widget('apply_record_tool')
        button_apl.connect('clicked', self.on_apply_record_tool_clicked)

    def on_add_record_tool_clicked(self, button):
        q = self.query
        if not q.add_record.get_property("sensitive"):
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
        q.apply_record.set_sensitive(True)

    def on_delete_record_tool_clicked(self, button):
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

    def on_apply_record_tool_clicked(self, button):
        q = self.query
        if not q.append_iter:
            return
        query = ""
        for field, value in q.filled_fields.iteritems():
            if query:
                query += ", "
            if not value.isdigit():
                value = "'%s'" % self.query.current_host.escape(value)
            query += "%s=%s" % (self.query.current_host.escape_field(field), value)
        if query:
            table, where, field, value, row_iter, fields = q.get_unique_where(q.last_source, return_fields=True)
            if self.query.last_th.host.__class__.__name__ == "sqlite_host":
                print (table, where, field, value, row_iter, fields)
                keys = []
                values = []
                for key, value in self.query.kv_list:
                    keys.append(key)
                    if type(value) == str:
                        values.append("'%s'" % value)
                    else:
                        values.append("%s" % value)
                update_query = "insert into `%s` (%s) values (%s)" % (table, ", ".join(keys), ", ".join(values))
            else:
                update_query = "insert into `%s` set %s" % (table, query)
            if not self.query.current_host.query(update_query, encoding=q.encoding):
                return False

            insert_id = self.query.current_host.insert_id()
            print "insert id: %r" % insert_id
            where_fields = map(lambda s: s.strip(), where.split(","))
            print "where fields: %r" % (where_fields, )
            print "select fields: %r" % (fields, )
            print "from %r" % ((table, where, field, value, row_iter), )
            if not where_fields:
                print "no possible key found to retrieve newly created record"
            else:
                th = self.query.current_host.current_db.tables[table]
                wc = []
                print 'where fields = ', where_fields
                for field in where_fields:
                    props = False
                    for field_object in th.fields:
                        if field_object.name == field:
                            props = field_object.row
                            print props
                    if props:
                        auto_increment = props['Extra'].find("auto_increment") != -1
                        if auto_increment:
                            value = insert_id
                        else:
                            if field in q.filled_fields:
                                # use filled value
                                value = "'%s'" % self.query.current_host.escape(q.filled_fields[field])
                            else:
                                # use field default value (maybe none)
                                value = props['Default']
                                if not value is None:
                                    value = "'%s'" % self.query.current_host.escape(value)
                        wc.append("%s=%s" % (self.query.current_host.escape_field(field), value))
                where = " and ".join(wc)
                print "select where: %r" % where
                if fields == ["*"]:
                    field_selector = "*"
                else:
                    field_selector = ", ".join(map(self.query.current_host.escape_field, fields))
                self.query.current_host.query("select %s from `%s` where %s limit 1" % (field_selector, table, where))
                result = self.query.current_host.handle.store_result().fetch_row(0)
                if len(result) < 1:
                    print "error: can't find modfied row!?"
                else:
                    row = result[0]
                    for index, value in enumerate(row):
                        if not value is None:
                            value = value.decode(q.encoding)
                        q.model.set_value(q.append_iter, index, value)
        else:
            q.model.remove(q.append_iter)
        q.append_iter = None
        q.apply_record.set_sensitive(False)
        return True