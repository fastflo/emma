import gtk
from MainNotebook import MainNotebook
from MainMenu import MainMenu


class MainWindow(gtk.Window):

    def __init__(self, emma):
        """
        @param emma: Emma
        """
        super(MainWindow, self).__init__()

        self.emma = emma

        self.accel_group = gtk.AccelGroup()
        self.add_accel_group(self.accel_group)

        self.main_notebook = MainNotebook(emma)
        self.main_notebook.show()
        self.message_notebook = gtk.Notebook()
        self.message_notebook.show()

        convbox = gtk.VBox(True, 0)
        self.connections_tv_container = gtk.ScrolledWindow()
        self.connections_tv_container.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.connections_tv_container.show()
        self.connections_tv_spinner = gtk.Spinner()
        convbox.pack_start(self.connections_tv_spinner, True, True)
        convbox.pack_end(self.connections_tv_container, True, True)
        convbox.show()

        vpaned1 = gtk.VPaned()

        vbox1 = gtk.VBox()
        vbox1.show()
        vbox1.pack_start(MainMenu(emma, self), False, False)

        hpaned1 = gtk.HPaned()
        hpaned1.pack1(convbox, False, True)
        hpaned1.pack2(self.main_notebook, True, True)
        hpaned1.set_position(200)
        hpaned1.show()

        vpaned1.pack1(hpaned1, False, True)
        vpaned1.pack2(self.message_notebook, False, True)
        vpaned1.set_position(600)
        vpaned1.show()

        vbox1.pack_start(vpaned1, True, True)

        self.status_bar = gtk.Statusbar()

        vbox1.pack_end(self.status_bar, False, False)
        vbox1.show()

        self.add(vbox1)

        self.set_position(gtk.WIN_POS_CENTER)
        self.resize(1024, 768)

        self.show_all()
        self.connections_tv_spinner.hide()
