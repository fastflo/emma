import gtk


class ApplyRecord(gtk.ToolButton):
    def __init__(self, query, emma):
        """
        @param query: QueryTab
        @param emma: Emma
        """
        super(ApplyRecord, self).__init__()
        self.emma = emma
        self.query = query

        self.set_label('Store Record')
        self.set_icon_name(gtk.STOCK_APPLY)
        self.set_tooltip_text('Store appended row')

        self.connect('clicked', self.on_clicked)

    def on_clicked(self, button):
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
        q.toolbar.apply_record.set_sensitive(False)
        return True
