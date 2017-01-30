import gobject
import gtk
import gc
import re
import time
from emmalib.Query import read_query, is_query_appendable, get_order_from_query
from emmalib.dialogs import show_message, confirm
from emmalib.widgets import ResultCellRenders


class ExecuteQuery(gtk.ToolButton):
    """
    @param query: QueryTab
    @param emma: Emma
    """
    def __init__(self, query, emma):
        super(ExecuteQuery, self).__init__()
        self.emma = emma
        self.query = query

        self.set_label('Execute Query')
        self.set_icon_name(gtk.STOCK_MEDIA_FORWARD)
        self.set_tooltip_text('Execute Query (F9, Ctrl+Enter)')

        self.connect('clicked', self.on_clicked)
        self.emma.events.connect('execute_query', self.on_event)

    def on_event(self, _, b, c):
        """

        @param _:
        @param b:
        @param c:
        """
        self.on_clicked(b, c)

    def on_clicked(self, _, query=None):
        """

        @param _:
        @param query:
        @return:
        """
        field_count = 0
        if not query:
            b = self.query.textview.get_buffer()
            text = b.get_text(b.get_start_iter(), b.get_end_iter())
        else:
            text = query

        self.query.current_host = host = self.query.current_host
        if not host:
            show_message(
                "error executing this query!",
                "could not execute query, because there is no selected host!"
            )
            return

        self.query.current_db = self.query.current_db
        if self.query.current_db:
            host.select_database(self.query.current_db)
        elif host.current_db:
            if not confirm(
                    "query without selected db",
                    """warning: this query tab has no database selected
                    but the host-connection already has the database '%s' selected.
                    the author knows no way to deselect this database.
                    do you want to continue?""" % host.current_db.name, self.emma.mainwindow):
                return

        update = False
        select = False
        self.query.editable = False

        # single popup
        self.query.toolbar.add_record.set_sensitive(False)
        self.query.toolbar.delete_record.set_sensitive(False)
        # per query buttons
        self.query.toolbar.add_record.set_sensitive(False)
        self.query.toolbar.delete_record.set_sensitive(False)
        self.query.toolbar.apply_record.set_sensitive(False)
        self.query.toolbar.local_search.set_sensitive(False)
        self.query.toolbar.remove_order.set_sensitive(False)
        self.query.toolbar.save_result_csv.set_sensitive(False)
        self.query.toolbar.save_result_sql.set_sensitive(False)

        affected_rows = 0
        last_insert_id = 0
        num_rows = 0

        query_time = 0
        download_time = 0
        display_time = 0
        query_count = 0
        total_start = time.time()

        # cleanup last query model and treeview
        for col in self.query.treeview.get_columns():
            self.query.treeview.remove_column(col)
        if self.query.model:
            self.query.model.clear()

        _start = 0
        while _start < len(text):
            # search query end
            query_start, end = read_query(text, _start)
            if query_start is None:
                break
            thisquery = text[query_start:end]
            print "about to execute query %r" % thisquery
            _start = end + 1

            thisquery.strip(" \r\n\t;")
            if not thisquery:
                continue  # empty query
            query_count += 1
            query_hint = re.sub("[\n\r\t ]+", " ", thisquery[:40])
            self.query.label.set_text("executing query %d %s..." % (query_count, query_hint))
            self.query.label.window.process_updates(False)

            appendable = False
            appendable_result = is_query_appendable(thisquery)
            if appendable_result:
                appendable = True
                self.query.editable = self.query.is_query_editable(thisquery, appendable_result)
            print "appendable: %s, editable: %s" % (appendable, self.query.editable)

            ret = host.query(thisquery, encoding=self.query.encoding)
            query_time += host.query_time

            # if stop on error is enabled
            if not ret:
                print "mysql error: %r" % (host.last_error, )
                message = "error at: %s" % host.last_error.replace(
                    "You have an error in your SQL syntax.  "
                    "Check the manual that corresponds to your "
                    "MySQL server version for the right syntax to use near ",
                    "")
                message = "error at: %s" % message.replace(
                    "You have an error in your SQL syntax; "
                    "check the manual that corresponds to your MySQL server "
                    "version for the right syntax to use near ", "")

                line_pos = 0
                pos = message.find("at line ")
                if pos != -1:
                    line_no = int(message[pos + 8:])
                    while 1:
                        line_no -= 1
                        if line_no < 1:
                            break
                        p = thisquery.find("\n", line_pos)
                        if p == -1:
                            break
                        line_pos = p + 1

                i = self.query.textview.get_buffer().get_iter_at_offset(query_start + line_pos)

                match = re.search("error at: '(.*)'", message, re.DOTALL)
                if match and match.group(1):
                    # set focus and cursor!
                    # print "search for ->%s<-" % match.group(1)
                    pos = text.find(
                        match.group(1),
                        query_start + line_pos,
                        query_start + len(thisquery)
                    )
                    if not pos == -1:
                        i.set_offset(pos)
                else:
                    match = re.match("Unknown column '(.*?')", message)
                    if match:
                        # set focus and cursor!
                        pos = thisquery.find(match.group(1))
                        if not pos == 1:
                            i.set_offset(query_start + pos)

                self.query.textview.get_buffer().place_cursor(i)
                self.query.textview.scroll_to_iter(i, 0.0)
                self.query.textview.grab_focus()
                self.query.label.set_text(re.sub("[\r\n\t ]+", " ", message))
                return

            field_count = host.handle.field_count()
            if field_count == 0:
                # query without result
                update = True
                affected_rows += host.handle.affected_rows()
                last_insert_id = host.handle.insert_id()
                continue

            # query with result
            self.query.append_iter = None
            self.query.toolbar.local_search.set_sensitive(True)
            self.query.toolbar.add_record.set_sensitive(appendable)
            self.query.toolbar.delete_record.set_sensitive(self.query.editable)
            select = True
            self.query.last_source = thisquery
            # get sort order!
            sortable = True  # todo
            current_order = get_order_from_query(thisquery)
            sens = False
            if len(current_order) > 0:
                sens = True
            self.query.toolbar.remove_order.set_sensitive(sens and sortable)

            sort_fields = dict()
            for c, o in current_order:
                sort_fields[c.lower()] = o
            self.query.label.set_text("downloading resultset...")
            self.query.label.window.process_updates(False)

            start_download = time.time()
            result = host.handle.store_result()
            download_time = time.time() - start_download
            if download_time < 0:
                download_time = 0

            self.query.label.set_text("displaying resultset...")
            self.query.label.window.process_updates(False)

            # store field info
            self.query.result_info = result.describe()
            num_rows = result.num_rows()

            for col in self.query.treeview.get_columns():
                self.query.treeview.remove_column(col)

            columns = [gobject.TYPE_STRING] * field_count
            self.query.model = gtk.ListStore(*columns)
            self.query.treeview.set_model(self.query.model)
            self.query.treeview.set_rules_hint(True)
            self.query.treeview.set_headers_clickable(True)
            for i in range(field_count):
                title = self.query.result_info[i][0].replace("_", "__").replace("[\r\n\t ]+", " ")
                text_renderer = gtk.CellRendererText()
                if self.query.editable:
                    text_renderer.set_property("editable", True)
                    text_renderer.connect("edited", self.query.on_query_change_data, i)
                l = self.query.treeview.insert_column_with_data_func(
                    -1, title, text_renderer, ResultCellRenders.render_mysql_string, i)

                col = self.query.treeview.get_column(l - 1)

                if self.emma.config.get_bool("result_view_column_resizable"):
                    col.set_resizable(True)
                else:
                    col.set_resizable(False)
                    col.set_min_width(int(self.emma.config.get("result_view_column_width_min")))
                    col.set_max_width(int(self.emma.config.get("result_view_column_width_max")))

                if sortable:
                    col.set_clickable(True)
                    col.connect("clicked", self.query.on_query_column_sort, i)
                    # set sort indicator
                    field_name = self.query.result_info[i][0].lower()
                    try:
                        sort_col = sort_fields[field_name]
                        col.set_sort_indicator(True)
                        if sort_col:
                            col.set_sort_order(gtk.SORT_ASCENDING)
                        else:
                            col.set_sort_order(gtk.SORT_DESCENDING)
                    except:
                        col.set_sort_indicator(False)
                else:
                    col.set_clickable(False)
                    col.set_sort_indicator(False)

            cnt = 0
            start_display = time.time()
            last_display = start_display
            for row in result.fetch_row(0):
                def to_string(f):
                    if type(f) == str:
                        f = f.decode(self.query.encoding, "replace")
                    elif f is None:
                        pass
                    else:
                        f = str(f)
                    return f
                self.query.model.append(map(to_string, row))
                cnt += 1
                if not cnt % 100 == 0:
                    continue

                now = time.time()
                if (now - last_display) < 0.2:
                    continue

                self.query.label.set_text("displayed %d rows..." % cnt)
                self.query.label.window.process_updates(False)
                last_display = now

            display_time = time.time() - start_display
            if display_time < 0:
                display_time = 0

        result = []
        if select:
            # there was a query with a result
            result.append("rows: %d" % num_rows)
            result.append("fields: %d" % field_count)
            self.query.toolbar.save_result_csv.set_sensitive(True)
            self.query.toolbar.save_result_sql.set_sensitive(True)
        if update:
            # there was a query without a result
            result.append("affected rows: %d" % affected_rows)
            result.append("insert_id: %d" % last_insert_id)
        total_time = time.time() - total_start
        result.append("| total time: %.2fs (query: %.2fs" % (total_time, query_time))
        if select:
            result.append("download: %.2fs display: %.2fs" % (download_time, display_time))
        result.append(")")

        self.query.label.set_text(' '.join(result))
        self.emma.blob_view.tv.set_editable(self.query.editable)
        self.emma.blob_view.blob_update.set_sensitive(self.query.editable)
        self.emma.blob_view.blob_load.set_sensitive(self.query.editable)
        # todo update_buttons()
        gc.collect()
        return True
