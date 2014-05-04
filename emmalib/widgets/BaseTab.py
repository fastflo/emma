import gtk
from Constants import *


class BaseTab(object):
    def __init__(self):
        self.tab_label = gtk.Label('Tab Name')
        self.tab_label.show()

        self.tab_label_hbox = gtk.HBox(False, 4)

        # add icon
        self.tab_label_icon = gtk.Image()
        self.tab_label_icon.set_from_file(os.path.join(icons_path, 'table.png'))
        self.tab_label_icon.show()
        self.tab_label_hbox.pack_start(self.tab_label_icon)

        # add label
        self.tab_label_hbox.pack_start(self.get_label())

        # add close tab button
        self.tab_label_close_img = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        self.tab_label_close_img.show()

        self.tab_label_close_button = gtk.Button()
        self.tab_label_close_button.set_relief(gtk.RELIEF_NONE)
        self.tab_label_close_button.set_focus_on_click(False)
        style = gtk.RcStyle()
        style.xthickness = 0
        style.ythickness = 0
        self.tab_label_close_button.modify_style(style)
        self.tab_label_close_button.set_tooltip_text('Close (Ctrl+W)')
        self.tab_label_close_button.show()
        self.tab_label_close_button.add(self.tab_label_close_img)

        self.tab_label_hbox.pack_end(self.tab_label_close_button)

    def get_label(self):
        return self.tab_label

    def get_ui(self):
        return None

    def get_label_ui(self):
        return self.tab_label_hbox

    def get_tab_close_button(self):
        return self.tab_label_close_button