import gtk


class NewQuery(gtk.ToolButton):
    """
    @param query: QueryTab
    @param emma: Emma
    """
    def __init__(self, query, emma):
        super(NewQuery, self).__init__()
        self.emma = emma
        self.query = query

        self.set_label('New Query')
        self.set_icon_name(gtk.STOCK_NEW)
        self.set_tooltip_text('New Query Tab (Ctrl+T)')

        self.connect('clicked', self.on_clicked)

    def on_clicked(self, _):
        """

        @param _:
        """
        self.emma.main_notebook.add_query_tab()
