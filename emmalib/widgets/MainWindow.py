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
from MainNotebook import MainNotebook
from MainMenu import MainMenu


class MainWindow(gtk.Window):

    def __init__(self, emma):
        """
        @param emma: Emma
        """
        super(MainWindow, self).__init__()

        self.emma = emma

        self.accel_group = gtk.AccelGroup()
        self.add_accel_group(self.accel_group)

        self.main_notebook = MainNotebook(emma)
        self.main_notebook.show()
        self.message_notebook = gtk.Notebook()
        self.message_notebook.show()

        emma.events.connect(
            'toggle_message_notebook_visible',
            lambda a, b: self.message_notebook.set_visible(
                    not self.message_notebook.get_visible()
                )
        )

        convbox = gtk.VBox(True, 0)
        self.connections_tv_container = gtk.ScrolledWindow()
        self.connections_tv_container.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.connections_tv_container.show()
        self.connections_tv_spinner = gtk.Spinner()
        convbox.pack_start(self.connections_tv_spinner, True, True)
        convbox.pack_end(self.connections_tv_container, True, True)
        convbox.show()

        vpaned1 = gtk.VPaned()

        vbox1 = gtk.VBox()
        vbox1.show()
        vbox1.pack_start(MainMenu(emma, self), False, False)

        hpaned1 = gtk.HPaned()
        hpaned1.pack1(convbox, False, True)
        hpaned1.pack2(self.main_notebook, True, True)
        hpaned1.set_position(200)
        hpaned1.show()

        vpaned1.pack1(hpaned1, False, True)
        vpaned1.pack2(self.message_notebook, False, True)
        vpaned1.set_position(600)
        vpaned1.show()

        vbox1.pack_start(vpaned1, True, True)

        self.status_bar = gtk.Statusbar()

        vbox1.pack_end(self.status_bar, False, False)
        vbox1.show()

        self.add(vbox1)

        self.set_position(gtk.WIN_POS_CENTER)
        self.resize(1024, 768)

        self.show_all()
        self.connections_tv_spinner.hide()
