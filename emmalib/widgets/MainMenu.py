import gtk
import gobject


class MainMenu(gtk.MenuBar):

    __gsignals__ = {
        'item-selected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,))
    }

    def __init__(self, emma):
        super(MainMenu, self).__init__()

        self.emma = emma

        self.file_menu = gtk.MenuItem('_File')
        self.file_menu.connect('activate', self.activated)
        self.file_menu.set_submenu(self.get_file_menu())
        self.file_menu.show()
        self.append(self.file_menu)

    def get_file_menu(self):
        menu = gtk.Menu()
        item1 = gtk.MenuItem()
        item1.set_name('aaa')
        item1.set_label('_AAA')
        item1.show()
        menu.append(item1)
        menu.show()
        return menu

    def activated(self, item):
        self.emit('item-selected', item)
        pass



