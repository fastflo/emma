import gtk


class TableFieldsPopUp(gtk.Menu):

    def __init__(self):
        super(TableFieldsPopUp, self).__init__()

        self.edit = gtk.ImageMenuItem(gtk.STOCK_EDIT)
        self.edit.set_name('edit')
        self.edit.set_label('Edit field')
        self.edit.set_always_show_image(True)
        self.append(self.edit)

        self.append(gtk.SeparatorMenuItem())

        self.drop = gtk.ImageMenuItem(gtk.STOCK_DELETE)
        self.drop.set_name('drop')
        self.drop.set_label('Drop field')
        self.drop.set_always_show_image(True)
        self.append(self.drop)

        self.show_all()

    def popup(self, parent_menu_shell, parent_menu_item, func, button, activate_time, data=None):
        super(TableFieldsPopUp, self).popup(parent_menu_shell, parent_menu_item, func, button, activate_time, data)