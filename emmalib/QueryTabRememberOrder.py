import re
import dialogs


class QueryTabRememberOrder:
    def __init__(self, query, emma):
        self.emma = emma
        self.query = query
        button = self.query.xml.get_widget('remember_order')
        button.connect('clicked', self.on_remember_order_clicked)

    def on_remember_order_clicked(self, button):
        query = self.emma.current_query.last_source
        if not query:
            return None, None, None, None, None
        current_order = self.query.get_order_from_query(query)
        result = self.query.is_query_appendable(query)
        if not result:
            return None, None, None, None, None
        table_list = result.group(7)
        table_list = table_list.replace(" join ", ",")
        table_list = re.sub("(?i)(?:order[ \t\r\n]by.*|limit.*|group[ \r\n\t]by.*|order[ \r\n\t]by.*|where.*)",
                            "", table_list)
        table_list = table_list.replace("`", "")
        tables = map(lambda s: s.strip(), table_list.split(","))

        if len(tables) > 1:
            dialogs.show_message("store table order", "can't store table order of multi-table queries!")
            return
        table = tables[0]

        print "---\ntable: %s order: %s" % (table, current_order)
        config_name = "stored_order_db_%s_table_%s" % (self.emma.current_host.current_db.name, table)
        print "config name %s" % config_name
        self.emma.config.config[config_name] = str(current_order)
        if not self.emma.current_host.current_db.name in self.emma.stored_orders:
            self.emma.stored_orders[self.emma.current_host.current_db.name] = {}
        self.emma.stored_orders[self.emma.current_host.current_db.name][table] = current_order
        self.emma.config.save()