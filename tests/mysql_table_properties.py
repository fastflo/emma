import gtk
from emmalib.providers.mysql import MySqlHost


class Win(gtk.Window):

    def __init__(self):
        super(Win, self).__init__()
        self.set_position(gtk.WIN_POS_CENTER)
        self.resize(640, 480)
        self.connect('destroy', lambda *args: gtk.main_quit())
        self.host = None
        self.table = None
        self.db_connect()

        tp = self.table.get_table_properties_widget()
        if tp:
            self.add(tp)
            tp.update()

        self.show_all()

    def db_connect(self):
        _db = 'test'
        _tb = 'aaa'
        self.host = MySqlHost(None, None, 'Localhost', 'localhost', 3306, 'root', 'root', '', 0)
        self.host.connect()
        self.host.use_db(_db)
        self.host.databases[_db].refresh()
        self.host.databases[_db].tables[_tb].refresh()
        self.table = self.host.databases[_db].tables[_tb]
        self.table.refresh()


w = Win()
gtk.main()