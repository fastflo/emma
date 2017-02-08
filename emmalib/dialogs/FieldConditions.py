import gtk

import re

from emmalib import dialogs
from emmalib import re_src_after_order
from emmalib import re_src_query_order


class FieldConditions(gtk.Window):
    """
    Field Conditions Dialog
    """

    def __init__(self):
        super(FieldConditions, self).__init__()

    def get_selected_table(self):
        """
        :return:
        """
        path, column = self.connections_tv.get_cursor()
        depth = len(path)
        _iter = self.connections_tv.connections_model.get_iter(path)
        if depth == 3:
            return self.connections_tv.connections_model.get_value(_iter, 0)
        return None

    def on_fc_reset_clicked(self, button):
        """
        :param button:
        """
        for i in range(self.fc_count):
            self.fc_entry[i].set_text("")
            if i == 0:
                self.fc_combobox[i].set_active(0)
                self.fc_op_combobox[i].set_active(0)
            else:
                self.fc_combobox[i].set_active(-1)
                self.fc_op_combobox[i].set_active(-1)
            if i:
                self.fc_logic_combobox[i - 1].set_active(0)

    def on_template(self, button, t):
        """
        :param button:
        :param t:
        :return:
        """
        current_table = self.get_selected_table()

        if t.find("$table$") != -1:
            if not current_table:
                dialogs.show_message(
                    "info",
                    "no table selected!\nyou can't execute a template with $table$ in it, "
                    "if you have no table selected!")
                return
            t = t.replace("$table$", self.current_host.escape_table(current_table.name))

        pos = t.find("$primary_key$")
        if pos != -1:
            if not current_table:
                dialogs.show_message(
                    "info",
                    "no table selected!\nyou can't execute a template with $primary_key$ in it, "
                    "if you have no table selected!")
                return
            if not current_table.fields:
                dialogs.show_message(
                    "info",
                    "sorry, can't execute this template, because table '%s' has no fields!" %
                    current_table.name)
                return
            # is the next token desc or asc?
            result = re.search("(?i)[ \t\r\n]*(de|a)sc", t[pos:])
            order_dir = ""
            if result:
                o = result.group(1).lower()
                if o == "a":
                    order_dir = "asc"
                else:
                    order_dir = "desc"

            replace = ""
            while 1:
                primary_key = ""
                for name in current_table.field_order:
                    props = current_table.fields[name]
                    if props[3] != "PRI":
                        continue
                    if primary_key:
                        primary_key += " " + order_dir + ", "
                    primary_key += self.current_host.escape_field(name)
                if primary_key:
                    replace = primary_key
                    break
                key = ""
                for name in current_table.field_order:
                    props = current_table.fields[name]
                    if props[3] != "UNI":
                        continue
                    if key:
                        key += " " + order_dir + ", "
                    key += self.current_host.escape_field(name)
                if key:
                    replace = key
                    break
                replace = self.current_host.escape_field(current_table.field_order[0])
                break
            t = t.replace("$primary_key$", replace)

        if t.find("$field_conditions$") != -1:
            if not self.field_conditions_initialized:
                self.field_conditions_initialized = True
                self.fc_count = 4
                self.fc_window = self.xml.get_widget("field_conditions")
                table = self.xml.get_widget("fc_table")
                table.resize(1 + self.fc_count, 4)
                self.fc_entry = []
                self.fc_combobox = []
                self.fc_op_combobox = []
                self.fc_logic_combobox = []
                for i in range(self.fc_count):
                    self.fc_entry.append(gtk.Entry())
                    self.fc_entry[i].connect(
                        "activate",
                        lambda *e: self.fc_window.response(gtk.RESPONSE_OK)
                    )
                    self.fc_combobox.append(gtk.combo_box_new_text())
                    self.fc_op_combobox.append(gtk.combo_box_new_text())
                    self.fc_op_combobox[i].append_text("=")
                    self.fc_op_combobox[i].append_text("<")
                    self.fc_op_combobox[i].append_text(">")
                    self.fc_op_combobox[i].append_text("!=")
                    self.fc_op_combobox[i].append_text("LIKE")
                    self.fc_op_combobox[i].append_text("NOT LIKE")
                    self.fc_op_combobox[i].append_text("ISNULL")
                    self.fc_op_combobox[i].append_text("NOT ISNULL")
                    if i:
                        self.fc_logic_combobox.append(gtk.combo_box_new_text())
                        self.fc_logic_combobox[i - 1].append_text("disabled")
                        self.fc_logic_combobox[i - 1].append_text("AND")
                        self.fc_logic_combobox[i - 1].append_text("OR")
                        table.attach(self.fc_logic_combobox[i - 1], 0, 1, i + 1, i + 2)
                        self.fc_logic_combobox[i - 1].show()
                    table.attach(self.fc_combobox[i], 1, 2, i + 1, i + 2)
                    table.attach(self.fc_op_combobox[i], 2, 3, i + 1, i + 2)
                    table.attach(self.fc_entry[i], 3, 4, i + 1, i + 2)
                    self.fc_combobox[i].show()
                    self.fc_op_combobox[i].show()
                    self.fc_entry[i].show()
            if not current_table:
                dialogs.show_message(
                    "info",
                    "no table selected!\nyou can't execute a template with "
                    "$field_conditions$ in it, if you have no table selected!")
                return

            last_field = []
            for i in range(self.fc_count):
                last_field.append(self.fc_combobox[i].get_active_text())
                self.fc_combobox[i].get_model().clear()
                if i:
                    self.fc_logic_combobox[i - 1].set_active(0)
            fc = 0
            for field_name in current_table.field_order:
                for k in range(self.fc_count):
                    self.fc_combobox[k].append_text(field_name)
                    if last_field[k] == field_name:
                        self.fc_combobox[k].set_active(fc)
                fc += 1
            if not self.fc_op_combobox[0].get_active_text():
                self.fc_op_combobox[0].set_active(0)
            if not self.fc_combobox[0].get_active_text():
                self.fc_combobox[0].set_active(0)

            answer = self.fc_window.run()
            self.fc_window.hide()
            if answer != gtk.RESPONSE_OK:
                return

            def field_operator_value(field, op, value):
                """
                :param field:
                :param op:
                :param value:
                :return:
                """
                if op == "ISNULL":
                    return "isnull(`%s`)" % field
                if op == "NOT ISNULL":
                    return "not isnull(`%s`)" % field
                eval_kw = "eval: "
                if value.startswith(eval_kw):
                    return "`%s` %s %s" % (field, op, value[len(eval_kw):])
                return "%s %s '%s'" % (
                    self.current_host.escape_field(field), op, self.current_host.escape(value)
                )

            conditions = "%s" % (
                field_operator_value(
                    self.fc_combobox[0].get_active_text(),
                    self.fc_op_combobox[0].get_active_text(),
                    self.fc_entry[0].get_text()
                )
            )
            for i in range(1, self.fc_count):
                if self.fc_logic_combobox[i - 1].get_active_text() == "disabled" \
                        or self.fc_combobox[i].get_active_text() == "" \
                        or self.fc_op_combobox[i].get_active_text() == "":
                    continue
                conditions += " %s %s" % (
                    self.fc_logic_combobox[i - 1].get_active_text(),
                    field_operator_value(
                        self.fc_combobox[i].get_active_text(),
                        self.fc_op_combobox[i].get_active_text(),
                        self.fc_entry[i].get_text()
                    )
                )
            t = t.replace("$field_conditions$", conditions)

        try:
            new_order = self.stored_orders[self.current_host.current_db.name][current_table.name]
            print "found stored order: %r" % (new_order,)
            query = t
            try:
                r = self.query_order_re
            except:
                r = self.query_order_re = re.compile(re_src_query_order)
            match = re.search(r, query)
            if match:
                before, order, after = match.groups()
                order = ""
                addition = ""
            else:
                match = re.search(re_src_after_order, query)
                if not match:
                    before = query
                    after = ""
                else:
                    before = query[0:match.start()]
                    after = match.group()
                addition = "\norder by\n\t"
            order = ""
            for col, o in new_order:
                if order:
                    order += ",\n\t"
                order += self.current_host.escape_field(col)
                if not o:
                    order += " desc"
            if order:
                new_query = ''.join([before, addition, order, after])
            else:
                new_query = re.sub("(?i)order[ \r\n\t]+by[ \r\n\t]+", "", before + after)

            t = new_query
        except:
            pass
        self.events.trigger('execute_query')
