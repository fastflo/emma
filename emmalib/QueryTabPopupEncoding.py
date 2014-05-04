import gtk


class QueryTabPopupEncoding(gtk.Menu):

    def __init__(self, query):
        """
        @param query: QueryTab
        """
        self.query = query

        super(QueryTabPopupEncoding, self).__init__()

        print self.query.emma.config.codings

        for key in self.query.emma.config.codings.keys():
            index, description = self.query.emma.config.codings[key]
            item = gtk.MenuItem(key, False)
            item.connect("activate", self.on_query_encoding_changed, (key, index))
            self.append(item)
            item.show()

        self.show_all()

    def on_query_encoding_changed(self, menuitem, data):
        self.query.set_query_encoding(data[0])

