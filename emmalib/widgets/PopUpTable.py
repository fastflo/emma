import gtk
import gobject


class PopUpTable(gtk.Menu):

    __gsignals__ = {
        'item-selected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,))
    }

    def __init__(self):
        super(PopUpTable, self).__init__()

        item = gtk.ImageMenuItem(gtk.STOCK_REFRESH)
        item.set_name('refresh_table')
        item.set_label('Refrest Table')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        item = gtk.ImageMenuItem(gtk.STOCK_CUT)
        item.set_name('truncate_table')
        item.set_label('Truncate Table')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        item = gtk.ImageMenuItem(gtk.STOCK_DELETE)
        item.set_name('drop_table')
        item.set_label('Drop Table')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        item = gtk.ImageMenuItem(gtk.STOCK_APPLY)
        item.set_name('check_table')
        item.set_label('Check Table')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        item = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
        item.set_name('repair_table')
        item.set_label('Repair Table')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        self.show_all()

    def activated(self, item):
        self.emit('item-selected', item)
        pass
