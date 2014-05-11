import gtk
import gobject
from ResultCellRenders import *


class ResultView(gtk.ScrolledWindow):

    def __init__(self):
        super(ResultView, self).__init__()

        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.tv_data_model = None
        self.tv_data = gtk.TreeView()
        self.tv_data.set_rules_hint(True)
        self.tv_data.set_model(self.tv_data_model)
        self.add(self.tv_data)
        self.data_loaded = False
        self.show_all()

    def load_data(self, result):
        if not result or self.data_loaded:
            return
        #
        #   Build list store with sort and data columns
        #   Make map of result column index, its display column and sort column
        #
        self.data_loaded = True
        columns = []
        sort_display_map = []
        i = 0
        ci = 0
        for t in result['types']:
            columns.append(t)
            sort_index = i
            disp_index = sort_index
            i += 1
            if t == gobject.TYPE_LONG or t == gobject.TYPE_INT or t == gobject.TYPE_FLOAT:
                columns.append(gobject.TYPE_STRING)
                disp_index = i
                i += 1
            sort_display_map.append((ci, sort_index, disp_index))
            ci += 1
        #
        #   Add it all to model and in treeview
        #
        self.tv_data_model = gtk.ListStore(*columns)
        self.tv_data.set_model(self.tv_data_model)
        #
        #   Add treeview columns according to previously built index/sort/data map
        #
        for column_index, sort_index, disp_index in sort_display_map:
            title = result['cols'][column_index].replace("_", "__").replace("[\r\n\t ]+", " ")
            self.column_insert(title, sort_index, disp_index)

        #
        #   Fill in List store with data
        #   In case of long and int columns - two columns added
        #   to make sorting and rendering properly
        #
        for row in result['rows']:
            model_row = []
            for col in result['cols']:
                ci = result['cols'].index(col)
                if result['types'][ci] == gobject.TYPE_LONG:
                    if row[col] is None:
                        v = 0
                    else:
                        v = long(row[col])
                    model_row.append(v)
                    model_row.append(row[col])
                elif result['types'][ci] == gobject.TYPE_INT:
                    if row[col] is None:
                        v = 0
                    else:
                        v = int(row[col])
                    model_row.append(v)
                    model_row.append(row[col])
                elif result['types'][ci] == gobject.TYPE_FLOAT:
                    if row[col] is None:
                        v = 0
                    else:
                        v = float(row[col])
                    model_row.append(v)
                    model_row.append(row[col])
                elif result['types'][ci] == gobject.TYPE_STRING:
                    if row[col] is None:
                        #
                        #   Add as none
                        #
                        model_row.append(None)
                    else:
                        if type(row[col]) != str:
                            row[col] = str(row[col])
                        try:
                            #
                            #   Add as ascii
                            #
                            row[col].decode('ascii')
                            v = str(row[col])
                        except:
                            try:
                                #
                                #   Add as converted utf8
                                #
                                v = row[col].decode('utf-8')
                            except UnicodeError:
                                #
                                #   Can't convert to string
                                #   Then it might be a binary
                                #
                                v = '<BINARY>'
                        model_row.append(v)
            try:
                self.tv_data_model.append(model_row)
            except:
                pass

    def column_insert(self, title, sort_column_index, display_column_index):
        text_renderer = gtk.CellRendererText()
        ci = self.tv_data.insert_column_with_data_func(
            -1,
            title,
            text_renderer,
            render_mysql_string,
            display_column_index)
        col = self.tv_data.get_column(ci-1)
        col.set_sort_column_id(sort_column_index)

    def cleanup(self):
        self.data_loaded = False
        for col in self.tv_data.get_columns():
            self.tv_data.remove_column(col)
        if self.tv_data_model:
            self.tv_data_model.clear()
