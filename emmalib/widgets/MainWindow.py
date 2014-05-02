import gtk
import widgets


class MainWindow(gtk.Window):

    def __init__(self, emma):
        super(MainWindow, self).__init__()

        self.emma = emma

        self.main_notebook = gtk.Notebook()
        self.main_notebook.show()
        self.message_notebook = gtk.Notebook()
        self.message_notebook.show()
        self.connections_tv_container = gtk.ScrolledWindow()
        self.connections_tv_container.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.connections_tv_container.show()

        vpaned1 = gtk.VPaned()

        vbox1 = gtk.VBox()
        vbox1.pack_start(widgets.MainMenu(self.emma), False, False)
        hpaned1 = gtk.HPaned()
        hpaned1.pack1(self.connections_tv_container, False, True)
        hpaned1.pack2(self.main_notebook, True, True)
        hpaned1.set_position(200)
        hpaned1.show()
        vbox1.pack_start(hpaned1, True, True)

        vpaned1.pack1(vbox1, False, True)
        vpaned1.pack2(self.message_notebook, False, True)
        vpaned1.set_position(600)
        vpaned1.show()

        self.add(vpaned1)

        self.set_position(gtk.WIN_POS_CENTER)
        self.resize(1024, 768)

        self.show_all()

