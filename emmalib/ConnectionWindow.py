import os
import gtk
import gtk.glade
import sys


class ConnectionWindow:
    def __init__(self, emma=None):
        from emmalib import emma_path

        self.host = None
        self.emma = emma
        self.cw_mode = None
        self.cw_props = ["name", "host", "port", "user", "password", "database"]
        self.glade_file = os.path.join(emma_path, "ConnectionWindow.glade")
        self.glade = gtk.glade.XML(self.glade_file)
        self.window = self.gw('connection_window')
        print self.window
        self.gw("cw_apply_button").connect("clicked", self.on_apply_button_clicked)
        self.gw("cw_test_button").connect("clicked", self.on_test_button_clicked)
        self.show_mysql()
        self.gw("cmb_connection_type").connect("changed", self.on_connection_type_changed)
        if self.emma:
            self.window.connect('destroy', self.on_window_close)
            self.window.connect('delete-event', self.on_window_delete)
            self.gw("cw_abort_button").connect("clicked", self.on_window_close)
        else:
            self.window.connect('destroy', lambda *a: gtk.main_quit())
            self.gw("cw_abort_button").connect("clicked", lambda *a: gtk.main_quit())
            self.window.show()

    def on_window_delete(self, *args):
        self.on_window_close(args)
        return True

    def on_window_close(self, obj):
        self.window.hide()
        return False

    def show_mysql(self):
        self.gw("cmb_connection_type").set_active(0)
        for n in ['host', 'port', 'user', 'password', 'database']:
            self.gw("lb_%s" % n).show()
            self.gw("tb_%s" % n).show()
        self.gw("lb_datafile").hide()
        self.gw("fcb_datafile").hide()

    def show_sqlite(self):
        self.gw("cmb_connection_type").set_active(1)
        for n in ['host', 'port', 'user', 'password', 'database']:
            self.gw("lb_%s" % n).hide()
            self.gw("tb_%s" % n).hide()
        self.gw("lb_datafile").show()
        self.gw("fcb_datafile").show()

    def on_connection_type_changed(self, cmb):
        if cmb.get_active() == 0:
            self.show_mysql()
        else:
            self.show_sqlite()

    def gw(self, wn):
        return self.glade.get_widget(wn)

    def show(self, mode):
        if mode == "edit":
            self.window.set_title('Edit connection')
            if self.host.__class__.__name__ == 'MySqlHost':
                self.gw("tb_name").set_text(self.host.name)
                self.gw("tb_host").set_text(self.host.host)
                self.gw("tb_port").set_text(self.host.port)
                self.gw("tb_user").set_text(self.host.user)
                self.gw("tb_password").set_text(self.host.password)
                self.gw("tb_database").set_text(self.host.database)
                self.show_mysql()
            else:
                self.gw("fcb_datafile").set_title(self.host.name)
                self.show_sqlite()
        else:
            self.window.set_title('New connection')
            for n in ['name', 'host', 'port', 'user', 'password', 'database']:
                self.gw("tb_%s" % n).set_text('')

        self.cw_mode = mode
        self.window.show()

    def validate_mysql(self):
        if not self.gw('tb_name').get_text():
            self.alert('Please enter connection name!')
            return False

        #all is fine
        return True

    def on_apply_button_clicked(self, *args):
        if self.gw("cmb_connection_type").get_active() == 0:
            if not self.validate_mysql():
                return
            if self.cw_mode == "new":
                data = []
                for n in self.cw_props:
                    data.append(self.gw("tb_%s" % n).get_text())
                print data
                if not data[0]:
                    self.window.hide()
                    return
                if self.emma:
                    self.emma.add_mysql_host(*data)
            else:
                self.host.name = self.gw("tb_name").get_text()
                self.host.host = self.gw("tb_host").get_text()
                self.host.port = self.gw("tb_port").get_text()
                self.host.user = self.gw("tb_user").get_text()
                self.host.password = self.gw("tb_password").get_text()
                self.host.database = self.gw("tb_database").get_text()
        else:
            self.alert('Save SQLite')

        self.window.hide()

        if self.emma:
            self.emma.save_config()

    def on_test_button_clicked(self, *args):
        if self.gw("cmb_connection_type").get_active() == 0:
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
                    port = self.gw('tb_port').get_text()
                    if not port:
                        port = '3306'
                    data[widget_map.get(n, n)] = int(port)
                else:
                    data[widget_map.get(n, n)] = self.gw("tb_%s" % n).get_text()
            try:
                handle = _mysql.connect(**data)
            except _mysql.DatabaseError as err:
                self.alert(err.message)
                self.alert(
                    "could not connect to host <b>%s</b> with user <b>%s</b> and password <b>%s</b>:\n<i>%s</i>" % (
                        data["host"],
                        data["user"],
                        data["passwd"],
                        sys.exc_value
                    )
                )
                return
            self.alert(
                "successfully connected to host <b>%s</b> with user <b>%s</b>!" % (
                    data["host"],
                    data["user"]
                )
            )
            handle.close()
        else:
            self.alert('Test SQLite')

    @staticmethod
    def alert(text):
        md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_OTHER, gtk.BUTTONS_CLOSE, text)
        md.run()
        md.destroy()


if __name__ == "__main__":
    cw = ConnectionWindow()
    cw.show('new')
    gtk.main()