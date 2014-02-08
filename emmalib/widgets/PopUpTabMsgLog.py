import gtk
import gobject


class PopUpTabMsgLog(gtk.Menu):

    __gsignals__ = {
        'item-selected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,))
    }

    def __init__(self):
        super(PopUpTabMsgLog, self).__init__()

        item = gtk.ImageMenuItem(gtk.STOCK_CLEAR)
        item.set_name('clear_messages')
        item.set_label('Clear messages')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        self.show_all()

    def activated(self, item):
        self.emit('item-selected', item)
        pass
