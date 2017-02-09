"""
Base tab - used as parent for all Emma tabs
"""
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

import os
import gtk

from emmalib import icons_path


class BaseTab(object):
    """
    Base tab - used as parent for all Emma tabs
    """
    def __init__(self):
        self.tab_label = gtk.Label('Tab Name')
        self.tab_label.show()

        self.ui = None

        self.tab_label_hbox = gtk.HBox(False, 4)

        # add icon
        self.tab_label_icon = gtk.Image()
        self.tab_label_icon.set_from_file(os.path.join(icons_path, 'table.png'))
        self.tab_label_icon.show()
        self.tab_label_hbox.pack_start(self.tab_label_icon)

        # add label
        self.tab_label_hbox.pack_start(self.get_label())

        # add close tab button
        self.tab_label_close_img = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        self.tab_label_close_img.show()

        self.tab_label_close_button = gtk.Button()
        self.tab_label_close_button.set_relief(gtk.RELIEF_NONE)
        self.tab_label_close_button.set_focus_on_click(False)
        style = gtk.RcStyle()
        style.xthickness = 0
        style.ythickness = 0
        self.tab_label_close_button.modify_style(style)
        self.tab_label_close_button.set_tooltip_text('Close (Ctrl+W)')
        self.tab_label_close_button.show()
        self.tab_label_close_button.add(self.tab_label_close_img)

        self.tab_label_hbox.pack_end(self.tab_label_close_button)

    def get_label(self):
        """
        :return: gtk.Label
        """
        return self.tab_label

    def get_ui(self):
        """
        :return:
        """
        return self.ui

    def get_label_ui(self):
        """
        :return: gtk.HBox
        """
        return self.tab_label_hbox

    def get_tab_close_button(self):
        """
        :return: gtk.Button
        """
        return self.tab_label_close_button
