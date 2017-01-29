# -*- coding: utf-8 -*-
# emma
#
# Copyright (C) 2006 Florian Schmidt (flo@fastflo.de)
#               2014 Nickolay Karnaukhov (mr.electronick@gmail.com)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

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

        self.emma.mainwindow.connect('key_release_event', self.on_mainwindow_key_release_event)
        self.emma.mainwindow.connect('key_press_event', self.on_mainwindow_key_press_event)

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
            self.emma.events.emit('execute_query', None, None)

        if event.keyval == keysyms.Return and self.if_ctrl():
            self.emma.events.emit('execute_query')
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
        # if event.keyval == keysyms.m and self.if_ctrl():
        #     self.toggle_message_notebook(None, _window)
        # if event.keyval == keysyms.h and self.if_ctrl():
        #     self.toggle_connections_tv(None, _window)

        if event.keyval == keysyms.Control_L:
            self.left_control_key_is_pressed = False
        if event.keyval == keysyms.Control_R:
            self.right_control_key_is_pressed = False
        return True

    def if_ctrl(self):
        return self.left_control_key_is_pressed or self.right_control_key_is_pressed

    def toggle_connections_tv(self, item, window):
        window.connections_tv_container.set_visible(
            not window.connections_tv_container.get_visible())

    def toggle_message_notebook(self, item, window):
        window.message_notebook.set_visible(
            not window.message_notebook.get_visible())
