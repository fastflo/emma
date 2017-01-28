import gtk
import dialogs


class RenameQuery(gtk.ToolButton):
    def __init__(self, query, emma):
        """
        @param query: QueryTab
        @param emma: Emma
        """
        super(RenameQuery, self).__init__()
        self.emma = emma
        self.query = query

        self.set_label('Rename Query')
        self.set_icon_name(gtk.STOCK_BOLD)
        self.set_tooltip_text('Rename Query Tab')

        self.connect('clicked', self.on_clicked)

    def on_clicked(self, button):
        label = self.query.get_label()
        new_name = dialogs.input_dialog("Rename tab", "Please enter the new name of this tab:",
                                        label.get_text(),
                                        self.emma.mainwindow)
        if new_name is None:
            return
        if new_name == "":
            self.query.last_auto_name = None
            self.query.update_db_label()
            return
        self.query.user_rename(new_name)

    def user_rename(self, new_name):
        # tab_widget = self.nb.get_tab_label(self.page)
        self.query.get_label().set_text(new_name)

