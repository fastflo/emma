import gtk
import gobject


class PopUpDatabase(gtk.Menu):
    __gsignals__ = {
        'item-selected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,))
    }

    def __init__(self):
        super(PopUpDatabase, self).__init__()

        item = gtk.ImageMenuItem(gtk.STOCK_REFRESH)
        item.set_name('refresh_database')
        item.set_label('Refrest Database')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        item = gtk.ImageMenuItem(gtk.STOCK_DELETE)
        item.set_name('drop_database')
        item.set_label('Drop Database')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        self.append(gtk.SeparatorMenuItem())

        item = gtk.ImageMenuItem(gtk.STOCK_NEW)
        item.set_name('new_table')
        item.set_label('New Table')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        item = gtk.ImageMenuItem(gtk.STOCK_APPLY)
        item.set_name('check_tables')
        item.set_label('Check Tables')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        item = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
        item.set_name('repair_tables')
        item.set_label('Repair Tables')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        self.show_all()

    def activated(self, item):
        self.emit('item-selected', item)
        pass
