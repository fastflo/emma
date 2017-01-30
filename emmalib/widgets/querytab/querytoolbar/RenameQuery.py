import gtk
from emmalib import dialogs


class RenameQuery(gtk.ToolButton):
    """
    @param query: QueryTab
    @param emma: Emma
    """
    def __init__(self, query, emma):
        super(RenameQuery, self).__init__()
        self.emma = emma
        self.query = query

        self.set_label('Rename Query')
        self.set_icon_name(gtk.STOCK_BOLD)
        self.set_tooltip_text('Rename Query Tab')

        self.connect('clicked', self.on_clicked)

    def on_clicked(self, _):
        """

        @param _:
        @return:
        """
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
        self.user_rename(new_name)

    def user_rename(self, new_name):
        # tab_widget = self.nb.get_tab_label(self.page)
        """

        @param new_name:
        """
        self.query.get_label().set_text(new_name)

