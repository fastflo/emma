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


class MainMenu(gtk.MenuBar):

    __gsignals__ = {
        'item-selected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,))
    }

    def __init__(self, emma, mainwindow):
        """
        @param emma: Emma
        """
        super(MainMenu, self).__init__()

        self.emma = emma

        #
        #   FILE
        #
        self.file_menu = gtk.MenuItem('_File')

        file_menu_submenu = gtk.Menu()

        self.execute_query_from_disk = gtk.MenuItem('Execute Query From Disk')
        self.execute_query_from_disk.show()
        file_menu_submenu.append(self.execute_query_from_disk)

        sep1 = gtk.SeparatorMenuItem()
        sep1.show()
        file_menu_submenu.append(sep1)

        self.reload_plugins = gtk.MenuItem('Reload Plugins')
        self.reload_plugins.show()
        file_menu_submenu.append(self.reload_plugins)

        self.reread_config = gtk.MenuItem('Reload Config')
        self.reread_config.show()
        file_menu_submenu.append(self.reread_config)

        # sep2 = gtk.SeparatorMenuItem()
        # sep2.show()
        # file_menu_submenu.append(sep2)
        #
        # save_workspace = gtk.MenuItem('Save Workspace')
        # save_workspace.show()
        # file_menu_submenu.append(save_workspace)
        #
        # restore_workspace = gtk.MenuItem('Restore Workspace')
        # restore_workspace.show()
        # file_menu_submenu.append(restore_workspace)

        sep3 = gtk.SeparatorMenuItem()
        sep3.show()
        file_menu_submenu.append(sep3)

        self.quit_button = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        self.quit_button.show()
        file_menu_submenu.append(self.quit_button)

        file_menu_submenu.show()

        self.file_menu.set_submenu(file_menu_submenu)
        self.file_menu.show()
        self.append(self.file_menu)

        #
        #   VIEW
        #

        self.view_menu = gtk.MenuItem('_View')
        view_menu_submenu = gtk.Menu()

        self.show_connections_tree = gtk.CheckMenuItem('Show Connections')
        key, mod = gtk.accelerator_parse("<Control>H")
        self.show_connections_tree.add_accelerator("activate", mainwindow.accel_group, key, mod, gtk.ACCEL_VISIBLE)
        self.show_connections_tree.connect("activate", self.emma.toggle_connections_tv, mainwindow)
        self.show_connections_tree.set_active(True)
        self.show_connections_tree.show()
        view_menu_submenu.append(self.show_connections_tree)

        self.show_message_notebook = gtk.CheckMenuItem('Show Messages Bar')
        key, mod = gtk.accelerator_parse("<Control>M")
        self.show_message_notebook.add_accelerator("activate", mainwindow.accel_group, key, mod, gtk.ACCEL_VISIBLE)
        self.show_message_notebook.connect("activate", self.emma.toggle_message_notebook, mainwindow)
        self.show_message_notebook.set_active(True)
        self.show_message_notebook.show()
        view_menu_submenu.append(self.show_message_notebook)

        view_menu_submenu.show()
        self.view_menu.set_submenu(view_menu_submenu)
        self.append(self.view_menu)

        #
        #   HELP
        #
        self.help_menu = gtk.MenuItem('_Help')
        help_menu_submenu = gtk.Menu()

        self.changelog = gtk.MenuItem('Changelog')
        self.changelog.show()
        help_menu_submenu.append(self.changelog)

        self.about = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
        self.about.show()
        help_menu_submenu.append(self.about)

        help_menu_submenu.show()

        self.help_menu.set_right_justified(True)
        self.help_menu.set_submenu(help_menu_submenu)
        self.help_menu.show()

        self.append(self.help_menu)

        self.show()

        self.execute_query_from_disk.connect('activate', self.emma.on_execute_query_from_disk_activate)
        self.reload_plugins.connect('activate', self.on_reload_plugins_activate)
        self.reread_config.connect('activate', self.on_reread_config_activate)
        #self.save_workspace.connect('activate', self.on_save_workspace_activate)
        #self.restore_workspace.connect('activate', self.on_restore_workspace_activate)
        self.quit_button.connect('activate', self.on_quit_activate)

        self.changelog.connect('activate', self.on_changelog_activate)
        self.about.connect('activate', self.on_about_activate)

    def activated(self, item):
        self.emit('item-selected', item)
        pass

    def on_reload_plugins_activate(self, item):
        self.emit('item-selected', item)
        self.emma.unload_plugins()
        self.emma.load_plugins()

    def on_reread_config_activate(self, item):
        self.emit('item-selected', item)
        self.emma.config.load()

    def on_about_activate(self, item):
        self.emit('item-selected', item)
        self.emma.about_dialog.run()
        self.emma.about_dialog.hide()

    def on_changelog_activate(self, item):
        self.emit('item-selected', item)
        self.emma.changelog_dialog.show()

    def on_quit_activate(self, item):
        self.emit('item-selected', item)
        gtk.main_quit()



