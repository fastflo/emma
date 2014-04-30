import gtk
from Constants import *


class BaseTab(object):
    def __init__(self):
        self.tab_label = gtk.Label('Tab Name')
        self.tab_label.show()
        self.ui = None

        self.tab_label_hbox = gtk.HBox()

        # add icon
        self.tab_label_icon = gtk.Image()
        self.tab_label_icon.set_from_file(os.path.join(icons_path, 'table.png'))
        self.tab_label_icon.show()
        self.tab_label_hbox.pack_start(self.tab_label_icon)

        # add label
        self.tab_label_label_ebox = gtk.EventBox()
        self.tab_label_label_ebox.add(self.get_label())
        self.tab_label_label_ebox.show()
        #tab_label_label_ebox.connect('button_release_event', self.on_query_tab_label_button_clicked)
        self.tab_label_hbox.pack_start(self.tab_label_label_ebox)

        # add close tab button
        self.tab_label_close_ebox = gtk.EventBox()
        self.tab_label_close_img = gtk.Image()
        self.tab_label_close_img.set_from_stock(gtk.STOCK_CLOSE, 1)
        self.tab_label_close_img.show()
        self.tab_label_close_ebox.add(self.tab_label_close_img)
        self.tab_label_close_ebox.show()
        self.tab_label_hbox.pack_end(self.tab_label_close_ebox)

    def get_label(self):
        return self.tab_label

    def get_ui(self):
        return self.ui

    def get_label_ui(self):
        return self.tab_label_hbox

    def close_tab_callback(self, callback):
        self.tab_label_close_ebox.connect('button_release_event', callback)