"""
Database Event Box
"""
import gtk


class DatabaseEventBox(gtk.EventBox):
    """
    Database event box
    """
    def __init__(self, query, emma):
        """
        @param query: QueryTab
        @param emma: Emma
        """
        super(DatabaseEventBox, self).__init__()

        self.emma = emma
        self.query = query

        self.connect('button-press-event', self.on_click)

        self.label = gtk.Label()
        self.label.set_alignment(0, 1)
        self.add(self.label)

    def set_label(self, text):
        """
        @param text: str
        @return:
        """
        self.label.set_label(text)

    def on_click(self, ebox, event):
        """
        @param ebox:
        @param event:
        @return:
        """
        qeury = self.query
        host = qeury.current_host
        database = qeury.current_db
        if qeury.last_path is not None:
            try:
                self.emma.connections_tv.connections_model.get_iter(qeury.last_path)
                self.emma.connections_tv.set_cursor(qeury.last_path)
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
            # print "host not found in connections list!"
            qeury.current_host = qeury.current_db = None
            qeury.update_db_label()
            return

        host_path = self.emma.connections_tv.connections_model.get_path(i)
        self.emma.connections_tv.scroll_to_cell(host_path,
                                                column=None, use_align=True,
                                                row_align=0.0, col_align=0.0)
        if database is None:
            self.emma.connections_tv.set_cursor(host_path)
            return
        k = self.emma.connections_tv.connections_model.iter_children(i)
        while k and self.emma.connections_tv.connections_model.iter_is_valid(k):
            if self.emma.connections_tv.connections_model[k][0] == database:
                break
            k = self.emma.connections_tv.connections_model.iter_next(k)
        else:
            # print "database not found in connections list!"
            qeury.current_db = None
            qeury.update_db_label()
            self.emma.connections_tv.set_cursor(host_path)
            return
        path = self.emma.connections_tv.connections_model.get_path(k)
        # self.connections_tv.scroll_to_cell(path,
        #                                    column=None, use_align=True,
        #                                    row_align=0.125, col_align=0.0)
        self.emma.connections_tv.set_cursor(path)
        return


