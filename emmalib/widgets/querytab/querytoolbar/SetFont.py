import gtk
import dialogs


class SetFont(gtk.ToolButton):
    def __init__(self, query, emma):
        """
        @param query: QueryTab
        @param emma: Emma
        """
        super(SetFont, self).__init__()
        self.emma = emma
        self.query = query

        self.set_label('Set Font')
        self.set_icon_name(gtk.STOCK_SELECT_FONT)
        self.set_tooltip_text('Set Query Font')

        self.connect('clicked', self.on_clicked)

    def on_clicked(self, button):
        d = self.emma.assign_once("query text font", gtk.FontSelectionDialog, "select query font")
        d.set_font_name(self.emma.config.get("query_text_font"))
        answer = d.run()
        d.hide()
        if not answer == gtk.RESPONSE_OK:
            return
        font_name = d.get_font_name()
        self.query.set_query_font(font_name)
        self.emma.config.config["query_text_font"] = font_name
        self.emma.config.save()
