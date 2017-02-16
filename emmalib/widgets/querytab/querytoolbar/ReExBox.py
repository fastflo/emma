"""
ReExBox
"""

# import gobject
import gtk


class ReExBox(gtk.ToolItem):
    """
    @param query: QueryTab
    @param emma: Emma
    """

    def __init__(self, query, emma):
        super(ReExBox, self).__init__()
        self.emma = emma
        self.query = query

        self.spin = gtk.SpinButton()
        self.spin.set_tooltip_text('Automatic Reexecution')
        self.spin.set_digits(1)
        # self.spin.set_increments(0.5, 0.5)
        self.spin.set_adjustment(gtk.Adjustment(0, 0, 99, 0.5, 10, 0))
        self.spin.set_value(0)
        self.add(self.spin)
        self.show_all()

        # self.set_label('New Query')
        # self.set_icon_name(gtk.STOCK_NEW)
        # self.set_tooltip_text('New Query Tab (Ctrl+T)')
        #
        # self.spin.connect('changed', self.on_change)

        # def on_change(self, button):
        #     value = button.get_value()
        #     if self.query.execution_timer_running:
        #         return
        #     self.query.execution_timer_running = True
        #     self.query.execution_timer_interval = value
        #     gobject.timeout_add(int(value * 1000), self.on_execution_timeout, button)

        # def on_execution_timeout(self, button):
        #     value = button.get_value()
        #     if value < 0.1:
        #         self.query.execution_timer_running = False
        #         return False
        #     if not self.query.on_execute_query_clicked():
        #         # stop on error
        #         button.set_value(0)
        #         value = 0
        #     if value != self.query.execution_timer_interval:
        #         self.query.execution_timer_running = False
        #         self.query.query_toolbar.reex.on_change(button)
        #         return False
        #     return True
