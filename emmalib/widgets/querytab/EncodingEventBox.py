"""
Encoding event box
"""
import gtk
from emmalib.widgets.querytab.QueryTabPopupEncoding import QueryTabPopupEncoding


class EncodingEventBox(gtk.EventBox):
    """

    @param query:
    @param emma:
    """

    def __init__(self, query, emma):
        """
        @param query: QueryTab
        @param emma: Emma
        """
        super(EncodingEventBox, self).__init__()

        self.emma = emma
        self.query = query
        self.query_encoding_menu = None

        self.connect('button-press-event', self.on_query_bottom_eventbox_button_press_event)

        self.label = gtk.Label()
        self.label.set_alignment(0, 1)
        self.add(self.label)

    def set_label(self, text):
        """

        @param text:
        """
        self.label.set_label(text)

    def on_query_bottom_eventbox_button_press_event(self, _, event):
        """

        @param _:
        @param event:
        """
        if not self.query_encoding_menu:
            self.query_encoding_menu = QueryTabPopupEncoding(self.query)
        self.query_encoding_menu.popup(None, None, None, event.button, event.time)
