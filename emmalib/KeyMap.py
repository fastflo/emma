import gtk
import gobject
from gtk import keysyms


class KeyMap(gobject.GObject):

    __gsignals__ = {
        'key-press': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gtk.gdk.Event,)),
        'key-release': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gtk.gdk.Event,)),
    }

    def __init__(self, emma):
        """
        @param emma: Emma
        """
        super(KeyMap, self).__init__()
        self.emma = emma
        self.left_control_key_is_pressed = False
        self.right_control_key_is_pressed = False

    def on_mainwindow_key_press_event(self, _window, event):
        self.emit('key-press', event)
        if event.keyval == keysyms.Control_L:
            self.left_control_key_is_pressed = True
        if event.keyval == keysyms.Control_R:
            self.right_control_key_is_pressed = True

    def on_mainwindow_key_release_event(self, _window, event):
        self.emit('key-release', event)
        #
        #   QueryTab stuff
        #
        if event.keyval == keysyms.F9:
            self.emma.current_query.on_execute_query_clicked()

        if event.keyval == keysyms.Return and self.if_ctrl():
            self.emma.current_query.on_execute_query_clicked()
            return False

        if event.keyval == keysyms.t and self.if_ctrl():
            self.emma.main_notebook.add_query_tab()
        if event.keyval == keysyms.w and self.if_ctrl():
            self.emma.main_notebook.close_current_tab()

        if event.keyval == keysyms.o and self.if_ctrl():
            self.emma.current_query.on_load_query_clicked(None)
        if event.keyval == keysyms.s and self.if_ctrl():
            self.emma.current_query.on_save_query_clicked(None)

        if event.keyval == keysyms.F3:
            self.emma.current_query.local_search_action.on_local_search_button_clicked(None, True)
        #
        #   Panel switches
        #
        if event.keyval == keysyms.m and self.if_ctrl():
            self.emma.mainwindow.message_notebook.set_visible(
                not self.emma.mainwindow.message_notebook.get_visible())
        if event.keyval == keysyms.h and self.if_ctrl():
            self.emma.mainwindow.connections_tv_container.set_visible(
                not self.emma.mainwindow.connections_tv_container.get_visible())

        if event.keyval == keysyms.Control_L:
            self.left_control_key_is_pressed = False
        if event.keyval == keysyms.Control_R:
            self.right_control_key_is_pressed = False
        return True

    def if_ctrl(self):
        return self.left_control_key_is_pressed or self.right_control_key_is_pressed