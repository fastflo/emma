import gtk


class QueryTabSetResultFont:

    def __init__(self, query, emma):
        """
        @param query: QueryTab
        @param emma: Emma
        """
        self.emma = emma
        self.query = query
        button = self.query.xml.get_widget('query_result_font')
        button.connect('clicked', self.on_query_result_font_clicked)

    def on_query_result_font_clicked(self, button):
        d = self.emma.assign_once("query result font", gtk.FontSelectionDialog, "select result font")
        d.set_font_name(self.emma.config.get("query_result_font"))
        answer = d.run()
        d.hide()
        if not answer == gtk.RESPONSE_OK:
            return
        font_name = d.get_font_name()
        self.query.set_result_font(font_name)
        self.emma.config.config["query_result_font"] = font_name
        self.emma.config.save()

