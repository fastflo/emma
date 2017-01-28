import gtk


class CloseQuery(gtk.ToolButton):
    def __init__(self, query, emma):
        """
        @param query: QueryTab
        @param emma: Emma
        """
        super(CloseQuery, self).__init__()
        self.emma = emma
        self.query = query

        self.set_label('Close Query')
        self.set_icon_name(gtk.STOCK_CLOSE)
        self.set_tooltip_text('Close Query Tab (Ctrl+W)')

        self.connect('clicked', self.on_clicked)

    def on_clicked(self, button):
        self.emma.main_notebook.close_query_tab()
