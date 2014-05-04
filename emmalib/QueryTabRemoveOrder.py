import re


class QueryTabRemoveOrder:
    def __init__(self, query, emma):
        """
        @param query: QueryTab
        @param emma: Emma
        """
        self.emma = emma
        self.query = query
        button = self.query.xml.get_widget('remove_order')
        button.connect('clicked', self.on_remove_order_clicked)

    def on_remove_order_clicked(self, button):
        query = self.query.last_source
        try:
            r = self.emma.query_order_re
        except:
            r = self.emma.query_order_re = re.compile(self.emma.re_src_query_order)
        match = re.search(r, query)
        if not match:
            return
        before, order, after = match.groups()
        new_query = re.sub("(?i)order[ \r\n\t]+by[ \r\n\t]+", "", before + after)
        self.query.set(new_query)
        self.emma.sort_timer_running = False
        self.emma.on_execute_query_clicked()

