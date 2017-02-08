"""
Close Query Button
"""
import gtk


class CloseQuery(gtk.ToolButton):
    """

    @param query: QueryTab
    @param emma: Emma
    """

    def __init__(self, query, emma):
        super(CloseQuery, self).__init__()
        self.emma = emma
        self.query = query

        self.set_label('Close Query')
        self.set_icon_name(gtk.STOCK_CLOSE)
        self.set_tooltip_text('Close Query Tab (Ctrl+W)')

        self.connect('clicked', self.on_clicked)

    def on_clicked(self, _):
        """

        @param _:
        """
        self.emma.main_notebook.close_query_tab(self, self.query)
