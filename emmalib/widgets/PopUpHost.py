import gtk
import gobject


class PopUpHost(gtk.Menu):

    __gsignals__ = {
        'item-selected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,))
    }

    def __init__(self):
        super(PopUpHost, self).__init__()

        self.menu_refresh_host = gtk.ImageMenuItem(gtk.STOCK_REFRESH)
        self.menu_refresh_host.set_name('refresh_host')
        self.menu_refresh_host.set_label('Refrest host')
        self.menu_refresh_host.set_always_show_image(True)
        self.menu_refresh_host.connect('activate', self.activated)
        self.append(self.menu_refresh_host)

        self.menu_modify_connection = gtk.ImageMenuItem(gtk.STOCK_EDIT)
        self.menu_modify_connection.set_name('modify_connection')
        self.menu_modify_connection.set_label('Modify Connection')
        self.menu_modify_connection.set_always_show_image(True)
        self.menu_modify_connection.connect('activate', self.activated)
        self.append(self.menu_modify_connection)

        self.menu_delete_connection = gtk.ImageMenuItem(gtk.STOCK_DELETE)
        self.menu_delete_connection.set_name('delete_connection')
        self.menu_delete_connection.set_label('Delete Connection')
        self.menu_delete_connection.set_always_show_image(True)
        self.menu_delete_connection.connect('activate', self.activated)
        self.append(self.menu_delete_connection)

        self.menu_new_connection = gtk.ImageMenuItem(gtk.STOCK_NEW)
        self.menu_new_connection.set_name('new_connection')
        self.menu_new_connection.set_label('New Connection')
        self.menu_new_connection.set_always_show_image(True)
        self.menu_new_connection.connect('activate', self.activated)
        self.append(self.menu_new_connection)

        item = gtk.SeparatorMenuItem()
        self.append(item)

        self.menu_new_database = gtk.ImageMenuItem(gtk.STOCK_NEW)
        self.menu_new_database.set_name('new_database')
        self.menu_new_database.set_label('New Database')
        self.menu_new_database.set_always_show_image(True)
        self.menu_new_database.connect('activate', self.activated)
        self.append(self.menu_new_database)

        self.show_all()

    def activated(self, item):
        self.emit('item-selected', item)
        pass
