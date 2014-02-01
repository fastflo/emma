import gtk
import gobject


class PopUpHost(gtk.Menu):

    __gsignals__ = {
        'item-selected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,))
    }

    def __init__(self):
        super(PopUpHost, self).__init__()

        item = gtk.ImageMenuItem(gtk.STOCK_REFRESH)
        item.set_name('refresh_host')
        item.set_label('Refrest host')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        item = gtk.ImageMenuItem(gtk.STOCK_EDIT)
        item.set_name('modify_connection')
        item.set_label('Modify Connection')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        item = gtk.ImageMenuItem(gtk.STOCK_DELETE)
        item.set_name('delete_connection')
        item.set_label('Delete Connection')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        item = gtk.ImageMenuItem(gtk.STOCK_NEW)
        item.set_name('new_connection')
        item.set_label('New Connection')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        item = gtk.SeparatorMenuItem()
        self.append(item)

        item = gtk.ImageMenuItem(gtk.STOCK_NEW)
        item.set_name('new_database')
        item.set_label('New Database')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        self.show_all()

    def activated(self, item):
        self.emit('item-selected', item)
        pass
