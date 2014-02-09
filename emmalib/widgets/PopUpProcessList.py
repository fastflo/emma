import gtk
import gobject


class PopUpProcessList(gtk.Menu):

    __gsignals__ = {
        'item-selected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,))
    }

    def __init__(self):
        super(PopUpProcessList, self).__init__()

        item = gtk.ImageMenuItem(gtk.STOCK_STOP)
        item.set_name('kill_process')
        item.set_label('Kill Process')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        self.show_all()

    def activated(self, item):
        self.emit('item-selected', item)
        pass

