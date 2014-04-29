from gtk import keysyms


class KeyMap:

    def __init__(self, emma):
        self.emma = emma
        self.left_control_key_is_pressed = False

    def on_mainwindow_key_press_event(self, _window, event):
        if event.keyval == keysyms.Control_L:
            self.left_control_key_is_pressed = True

    def on_mainwindow_key_release_event(self, _window, event):
        if event.keyval == keysyms.F3:
            self.emma.current_query.local_search_action.on_local_search_button_clicked(None, True)
            return True
        if event.keyval == keysyms.m and self.left_control_key_is_pressed:
            self.emma.message_notebook.set_visible(not self.emma.message_notebook.get_visible())
            return True
        if event.keyval == keysyms.h and self.left_control_key_is_pressed:
            self.emma.connections_tv_container.set_visible(not self.emma.connections_tv_container.get_visible())
            return True
        if event.keyval == keysyms.Control_L:
            self.left_control_key_is_pressed = False
            return True
