import gtk


class DatabaseEventBox(gtk.EventBox):
    def __init__(self, query, emma):
        """
        @param query: QueryTab
        @param emma: Emma
        """
        super(DatabaseEventBox, self).__init__()

        self.emma = emma
        self.query = query

        self.connect('button-press-event', self.on_query_db_eventbox_button_press_event)

        self.label = gtk.Label()
        self.label.set_alignment(0, 1)
        self.add(self.label)

    def set_label(self, text):
        self.label.set_label(text)

    def on_query_db_eventbox_button_press_event(self, ebox, event):
        q = self.query
        host = q.current_host
        db = q.current_db
        if q.last_path is not None:
            try:
                self.emma.connections_tv.connections_model.get_iter(q.last_path)
                self.emma.connections_tv.set_cursor(q.last_path)
                return
            except:
                # path was not valid
                pass

        i = self.emma.connections_tv.connections_model.get_iter_root()
        while i and self.emma.connections_tv.connections_model.iter_is_valid(i):
            if self.emma.connections_tv.connections_model[i][0] == host:
                break
            i = self.emma.connections_tv.connections_model.iter_next(i)
        else:
            print "host not found in connections list!"
            q.current_host = q.current_db = None
            q.update_db_label()
            return

        host_path = self.emma.connections_tv.connections_model.get_path(i)
        self.emma.connections_tv.scroll_to_cell(host_path, column=None, use_align=True, row_align=0.0, col_align=0.0)
        if db is None:
            self.emma.connections_tv.set_cursor(host_path)
            return
        k = self.emma.connections_tv.connections_model.iter_children(i)
        while k and self.emma.connections_tv.connections_model.iter_is_valid(k):
            if self.emma.connections_tv.connections_model[k][0] == db:
                break
            k = self.emma.connections_tv.connections_model.iter_next(k)
        else:
            print "database not found in connections list!"
            q.current_db = None
            q.update_db_label()
            self.emma.connections_tv.set_cursor(host_path)
            return
        path = self.emma.connections_tv.connections_model.get_path(k)
        #self.connections_tv.scroll_to_cell(path, column=None, use_align=True, row_align=0.125, col_align=0.0)
        self.emma.connections_tv.set_cursor(path)
        return


