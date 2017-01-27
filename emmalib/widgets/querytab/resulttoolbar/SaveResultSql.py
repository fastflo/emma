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
import dialogs
from Query import *


class SaveResultSql(gtk.ToolButton):

    def __init__(self, query, emma):
        """
        @param query: QueryTab
        @param emma: Emma
        """
        self.emma = emma
        self.query = query
        super(SaveResultSql, self).__init__()

        self.set_label('Save as SQL')
        self.set_icon_name(gtk.STOCK_SAVE_AS)
        self.set_tooltip_text('Save result as sql insert script')
        
        self.connect('clicked', self.on_save_result_sql_clicked)
        self.set_sensitive(False)

    def on_save_result_sql_clicked(self, button):
        title = "save results as sql insert script"
        d = self.emma.assign_once(
            "save results dialog",
            gtk.FileChooserDialog, title, self.emma.mainwindow, gtk.FILE_CHOOSER_ACTION_SAVE,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))

        d.set_default_response(gtk.RESPONSE_ACCEPT)
        answer = d.run()
        d.hide()
        if not answer == gtk.RESPONSE_ACCEPT:
            return
        filename = d.get_filename()
        if os.path.exists(filename):
            if not os.path.isfile(filename):
                dialogs.show_message(title, "%s already exists and is not a file!" % filename)
                return
            if not dialogs.confirm(
                    "overwrite file?",
                    "%s already exists! do you want to overwrite it?" % filename, self.emma.mainwindow):
                return
        q = self.query
        _iter = q.model.get_iter_first()
        indices = range(q.model.get_n_columns())

        # try to guess target table name from query
        table_name = ""
        query = self.query.last_source
        result = is_query_appendable(query)
        if result:
            table_list = result.group(7)
            table_list = table_list.replace(" join ", ",")
            table_list = re.sub("(?i)(?:order[ \t\r\n]by.*|limit.*|group[ \r\n\t]by.*|order[ \r\n\t]by.*|where.*)", "",
                                table_list)
            table_list = table_list.replace("`", "")
            tables = map(lambda s: s.strip(), table_list.split(","))
            table_name = "_".join(tables)
        table_name = dialogs.input_dialog(title, "Please enter the name of the target table:", table_name,
                                          self.emma.mainwindow)
        if table_name is None:
            return
        table_name = self.emma.current_host.escape_table(table_name)

        output_row = None
        try:
            fp = file(filename, "wb")
            fp.write("insert into %s values" % table_name)
            row_delim = "\n\t"
            while _iter:
                row = q.model.get(_iter, *indices)
                if not output_row:
                    output_row = range(len(row))
                for i, field in enumerate(row):
                    if field is None:
                        field = "NULL"
                    elif not field.isdigit():
                        field = "'%s'" % q.current_host.escape(field.encode(q.encoding))
                    output_row[i] = field
                fp.write("%s(%s)" % (row_delim, ",".join(output_row)))
                row_delim = ",\n\t"
                _iter = q.model.iter_next(_iter)
            fp.write("\n;\n")
            fp.close()
        except:
            dialogs.show_message(title, "error writing to file %s: %s" % (filename, sys.exc_value))

