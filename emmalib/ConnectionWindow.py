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

# import os
import gtk
import gtk.glade
import dialogs
from Constants import *


class ConnectionWindow:
    """
    @param emma: Emma
    """
    def __init__(self, emma=None):
        self.host = None
        self.emma = emma
        self.cw_mode = None
        self.text_fields = ["name", "host", "port", "user", "password", "database"]
        self.glade_file = os.path.join(emma_path, "ConnectionWindow.glade")
        self.glade = gtk.glade.XML(self.glade_file)
        self.window = self.connection_window
        self.cw_apply_button.connect("clicked", self.on_apply_button_clicked)
        self.cw_test_button.connect("clicked", self.on_test_button_clicked)
        self.show_mysql()
        self.cmb_connection_type.connect("changed", self.on_connection_type_changed)
        if self.emma:
            self.window.connect('destroy', self.on_window_close)
            self.window.connect('delete-event', self.on_window_delete)
            self.cw_abort_button.connect("clicked", self.on_window_close)
        else:
            self.window.connect('destroy', lambda *a: gtk.main_quit())
            self.cw_abort_button.connect("clicked", lambda *a: gtk.main_quit())
            self.window.show()

    def on_window_delete(self, *args):
        """
        :param args: []
        :return: bool
        """
        self.on_window_close(args)
        return True

    def on_window_close(self, _):
        """
        :param _: gtk.Window
        :return: bool
        """
        self.window.hide()
        return False

    def show_mysql(self):
        """
        Display MySQL settings
        """
        self.lb_provider_name.set_text('MySQL')
        self.cmb_connection_type.set_active(0)
        for n in ['host', 'port', 'user', 'password', 'database']:
            self.glade.get_widget("lb_%s" % n).show()
            self.glade.get_widget("tb_%s" % n).show()
        self.lb_datafile.hide()
        self.fcb_datafile.hide()
        self.lb_datafile_current.hide()
        self.lb_datafile_current_path.hide()
        self.cw_test_button.show()

    def show_sqlite(self):
        """
        Display SQLite settings
        """
        self.lb_provider_name.set_text('SQLite')
        self.cmb_connection_type.set_active(1)
        for n in ['host', 'port', 'user', 'password', 'database']:
            self.glade.get_widget("lb_%s" % n).hide()
            self.glade.get_widget("tb_%s" % n).hide()
        if self.cw_mode == "new":
            self.lb_datafile.show()
            self.fcb_datafile.show()
            self.lb_datafile_current.hide()
            self.lb_datafile_current_path.hide()
        else:
            self.lb_datafile.hide()
            self.fcb_datafile.hide()
            self.lb_datafile_current.show()
            self.lb_datafile_current_path.show()
        self.cw_test_button.hide()

    def cleanup(self):
        """
        Empty text fields
        """
        self.lb_provider_name.set_text('')
        for n in self.text_fields:
            self.glade.get_widget("tb_%s" % n).set_text('')

    def on_connection_type_changed(self, cmb):
        """
        :param cmb: gtk.ComboBox
        """
        if cmb.get_active() == 0:
            self.show_mysql()
        else:
            self.show_sqlite()

    def show(self, mode):
        """
        Show controls depending on mode
        :param mode: str
        """
        self.cleanup()
        if mode == "edit":
            self.cmb_connection_type.hide()
            self.lb_provider_name.show()
            self.window.set_title('Edit connection')
            if self.host.__class__.__name__ == 'MySqlHost':
                self.tb_name.set_text(self.host.name)
                self.tb_host.set_text(self.host.host)
                self.tb_port.set_text(self.host.port)
                self.tb_user.set_text(self.host.user)
                self.tb_password.set_text(self.host.password)
                self.tb_database.set_text(self.host.database)
                self.show_mysql()
            else:
                self.tb_name.set_text(self.host.name)
                self.lb_datafile.hide()
                self.fcb_datafile.hide()
                self.lb_datafile_current.show()
                self.lb_datafile_current_path.show()
                self.lb_datafile_current_path.set_text(self.host.name)
                self.show_sqlite()
        else:
            self.cmb_connection_type.show()
            self.lb_provider_name.hide()
            self.window.set_title('New connection')
            for n in ['name', 'host', 'port', 'user', 'password', 'database']:
                self.glade.get_widget("tb_%s" % n).set_text('')

        self.cw_mode = mode
        self.window.show()

    def validate_mysql(self):
        """
        Validate MySQL settings
        :return: bool
        """
        if not self.glade.get_widget('tb_name').get_text():
            dialogs.alert('Please enter connection name!')
            return False
        return True

    def on_apply_button_clicked(self, *_):
        """
        :param _: []
        :return:
        """
        if self.cmb_connection_type.get_active() == 0:
            if not self.validate_mysql():
                return
            if self.cw_mode == "new":
                data = []
                for n in self.text_fields:
                    data.append(self.glade.get_widget("tb_%s" % n).get_text())
                print data
                if not data[0]:
                    self.window.hide()
                    return
                if self.emma:
                    self.emma.connections_tv.add_mysql_host(*data)
            else:
                self.host.name = self.tb_name.get_text()
                self.host.host = self.tb_host.get_text()
                self.host.port = self.tb_port.get_text()
                self.host.user = self.tb_user.get_text()
                self.host.password = self.tb_password.get_text()
                self.host.database = self.tb_database.get_text()
        else:
            if self.cw_mode == "new":
                self.emma.connections_tv.add_sqlite(self.fcb_datafile.get_filename())
            else:
                pass

        self.window.hide()

        if self.emma:
            self.emma.config.save()

    def on_test_button_clicked(self, *_):
        """
        :param _: []
        :return: None
        """
        if self.cmb_connection_type.get_active() == 0:
            if not self.validate_mysql():
                return
            import _mysql
            data = {
                "connect_timeout": 6
            }
            widget_map = {
                "password": "passwd"
            }
            for n in ["host", "user", "password", "port"]:
                if n == 'port':
                    port = self.glade.get_widget('tb_port').get_text()
                    if not port:
                        port = '3306'
                    data[widget_map.get(n, n)] = int(port)
                else:
                    data[widget_map.get(n, n)] = self.glade.get_widget("tb_%s" % n).get_text()
            try:
                handle = _mysql.connect(**data)
            except _mysql.DatabaseError as err:
                print "_mysql.DatabaseError:", err.message
                dialogs.alert(
                    "could not connect to host <b>%s</b> with user <b>%s</b> "
                    "and password <b>%s</b>:\n<i>%s</i>\nMySQL error message:\n%s" % (
                        data["host"],
                        data["user"],
                        data["passwd"],
                        sys.exc_value,
                        err.message
                    )
                )
                return
            dialogs.alert(
                "successfully connected to host <b>%s</b> with user <b>%s</b>!" % (
                    data["host"],
                    data["user"]
                )
            )
            handle.close()
        else:
            dialogs.alert('Nothing to test')

    def __getattr__(self, name):
        widget = self.glade.get_widget(name)
        if widget is None:
            raise AttributeError(name)
        return widget
