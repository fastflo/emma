import gtk


class QueryTabTreeView(gtk.TreeView):
    def __init__(self, emma=None):
        """
        @param emma: Emma
        """
        self.emma = emma
        super(QueryTabTreeView, self).__init__()