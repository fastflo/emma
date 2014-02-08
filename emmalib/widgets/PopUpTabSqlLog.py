import gtk
import gobject


class PopUpTabSqlLog(gtk.Menu):

    __gsignals__ = {
        'item-selected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,))
    }

    def __init__(self):
        super(PopUpTabSqlLog, self).__init__()

        item = gtk.ImageMenuItem(gtk.STOCK_COPY)
        item.set_name('copy_sql_log')
        item.set_label('Copy')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        item = gtk.ImageMenuItem(gtk.STOCK_JUSTIFY_FILL)
        item.set_name('set_as_query_text')
        item.set_label('Set as query text')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        item = gtk.ImageMenuItem(gtk.STOCK_DELETE)
        item.set_name('delete_sql_log')
        item.set_label('Delete')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        item = gtk.ImageMenuItem(gtk.STOCK_CLEAR)
        item.set_name('clear_all_entries')
        item.set_label('Clear')
        item.set_always_show_image(True)
        item.connect('activate', self.activated)
        self.append(item)

        self.show_all()

    def activated(self, item):
        self.emit('item-selected', item)
        pass
