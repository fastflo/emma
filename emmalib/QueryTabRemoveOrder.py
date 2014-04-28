import re


class QueryTabRemoveOrder:
    def __init__(self, query, emma):
        self.emma = emma
        self.query = query
        button = self.query.xml.get_widget('remove_order')
        button.connect('clicked', self.on_remove_order_clicked)

    def on_remove_order_clicked(self, button):
        query = self.emma.current_query.last_source
        try:
            r = self.emma.query_order_re
        except:
            r = self.emma.query_order_re = re.compile(self.emma.re_src_query_order)
        match = re.search(r, query)
        if not match:
            return
        before, order, after = match.groups()
        new_query = re.sub("(?i)order[ \r\n\t]+by[ \r\n\t]+", "", before + after)
        self.emma.current_query.set(new_query)
        self.emma.sort_timer_running = False
        self.emma.on_execute_query_clicked()
