import gtk
#import emmalib.Config


class ConnectionsTreeView(gtk.TreeView):
    def __init__(self):
        print "ConnectionTreeView ctr"

        # create a TreeStore with one string column to use as the model
        self.treestore = gtk.TreeStore(str)

        # we'll add some data now - 4 rows with 3 child rows each
        for parent in range(4):
            piter = self.treestore.append(None, ['parent %i' % parent])
            for child in range(3):
                self.treestore.append(piter, ['child %i of parent %i' % (child, parent)])

        super(ConnectionsTreeView, self).__init__(self.treestore)

        self.tvcolumn = gtk.TreeViewColumn('Column 0')
        self.append_column(self.tvcolumn)
        self.cell = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)
        self.set_search_column(0)
        self.tvcolumn.set_sort_column_id(0)
        self.set_reorderable(True)


if __name__ != 'main':
    con = ConnectionsTreeView()

    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.connect("delete_event", lambda *x: gtk.main_quit())
    window.set_size_request(640, 480)
    window.set_position(gtk.WIN_POS_CENTER)
    window.add(con)
    window.show_all()
    gtk.main()