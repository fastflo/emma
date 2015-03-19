import gc
import bz2
import time
import datetime
from stat import *

import gtk.glade

from emmalib.Query import *
from emmalib.dialogs import show_message


class ExecuteQueryFromDisk:
    def __init__(self, emma):
        """
        @param emma: Emma
        """
        self.emma = emma
        #
        # PATHS
        #
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.glade_file = os.path.join(self.path, "ExecuteQueryFromDisk.glade")
        #
        # UI
        #
        self.glade = None
        self.window = None
        #
        # Commons
        #
        self.created_once = []
        self.using_compression = False
        self.last_query_line = ""
        self.query_from_disk = False
        self.read_one_query_started = False

    def show(self):
        self.glade = gtk.glade.XML(self.glade_file)
        self.glade.signal_autoconnect(self)
        self.window = self.glade.get_widget('execute_query_from_disk1')
        self.window.connect('destroy', lambda *args: self.hide)
        self.window.show()

    def hide(self):
        self.window.hide()

    def on_start_execute_from_disk_clicked(self, button):
        host = self.emma.connections_tv.current_host
        fc = self.glade.get_widget("eqfd_file_chooser")

        exclude = self.glade.get_widget("eqfd_exclude").get_active()
        exclude_regex = self.glade.get_widget("eqfd_exclude_entry").get_text()
        exclude = exclude and exclude_regex
        if exclude:
            try:
                exclude_regex = re.compile(exclude_regex, re.DOTALL)
            except:
                show_message(
                    "execute query from disk", "error compiling your regular expression: %s" % sys.exc_value)
                return

        filename = fc.get_filename()
        try:
            sbuf = os.stat(filename)
        except:
            show_message("execute query from disk", "%s does not exists!" % filename)
            return
        if not S_ISREG(sbuf.st_mode):
            show_message("execute query from disk", "%s exists, but is not a regular file!" % filename)
            return

        size = sbuf.st_size

        try:
            fp = bz2.BZ2File(filename, "r", 1024 * 8)
            self.last_query_line = fp.readline()
            self.using_compression = True
        except:
            self.using_compression = False
            fp = None

        if fp is None:
            try:
                fp = file(filename, "rb")
                self.last_query_line = fp.readline()
            except:
                show_message(
                    "execute query from disk",
                    "error opening query from file %s: %s" % (filename, sys.exc_value))
                return
        self.window.hide()

        start_line = self.glade.get_widget("eqfd_start_line").get_value()
        if start_line < 1:
            start_line = 1
        ui = self.glade.get_widget("eqfd_update_interval")
        update_interval = ui.get_value()
        if update_interval == 0:
            update_interval = 2

        p = self.glade.get_widget("execute_from_disk_progress")
        pb = self.glade.get_widget("exec_progress")
        offset_entry = self.glade.get_widget("edfq_offset")
        line_entry = self.glade.get_widget("eqfd_line")
        query_entry = self.glade.get_widget("eqfd_query")
        eta_label = self.glade.get_widget("eqfd_eta")
        append_to_log = self.glade.get_widget("eqfd_append_to_log").get_active()
        stop_on_error = self.glade.get_widget("eqfd_stop_on_error").get_active()
        limit_dbname = self.glade.get_widget("eqfd_db_entry").get_text()
        limit_db = self.glade.get_widget("eqfd_limit_db").get_active() and limit_dbname != ""

        if limit_db:
            limit_re = re.compile("(?is)^use[ \r\n\t]+`?" + re.escape(limit_dbname) + "`?|^create database[^`]+`?" +
                                  re.escape(limit_dbname) + "`?")
            limit_end_re = re.compile("(?is)^use[ \r\n\t]+`?.*`?|^create database")

        # last = 0
        _start = time.time()

        def update_ui(force=False, offset=0):
            global last_update
            now = time.time()
            if not force and now - last_update < update_interval:
                return
            last_update = now
            pos = offset
            f = float(pos) / float(size)
            expired = now - _start
            if not self.using_compression and expired > 10:
                sr = float(expired) / float(pos) * float(size - pos)
                remaining = " (%.0fs remaining)" % sr
                eta_label.set_text("eta: %-19.19s" % datetime.datetime.fromtimestamp(now + sr))
            else:
                remaining = ""
            query_entry.set_text(query[0:512])
            offset_entry.set_text("%d" % pos)
            line_entry.set_text("%d" % current_line)
            if f > 1.0:
                f = 1.0
            pb.set_fraction(f)
            pb_text = "%.2f%%%s" % (f * 100.0, remaining)
            pb.set_text(pb_text)
            self.emma.process_events()

        new_line = 1
        current_line = _start
        query = ""
        p.show()
        while time.time() - _start < 0.10:
            update_ui(True)
        self.query_from_disk = True
        line_offset = 0
        found_db = False
        while self.query_from_disk:
            current_line = new_line
            query, line_offset, new_line = self.read_one_query(
                fp, line_offset, current_line, update_ui, limit_db and not found_db, start_line)
            if current_line < start_line:
                current_line = start_line

            if query is None:
                break

            if limit_db:
                if not found_db:
                    first = query.lstrip("\r\n\t ")[0:15].lower()
                    if (first[0:3] == "use" or first == "create database") and limit_re.search(query):
                        found_db = True
                else:
                    if limit_end_re.search(query) and not limit_re.search(query):
                        found_db = False

            update_ui(False, fp.tell())
            if not limit_db or found_db:
                if exclude and exclude_regex.match(query):
                    print "skipping query %r" % query[0:80]
                elif not host.query(query, True, append_to_log) and stop_on_error:
                    show_message(
                        "execute query from disk",
                        "an error occoured. maybe remind the line number and press cancel to close this dialog!")
                    self.query_from_disk = False
                    break
        query = ""
        update_ui(True, fp.tell())
        fp.close()
        if not self.query_from_disk:
            show_message("execute query from disk",
                                 "aborted by user whish - click cancel again to close window")
            return
        else:
            show_message("execute query from disk", "done!")
        p.hide()

    def on_cancel_execute_from_disk_clicked(self, button):
        if not self.query_from_disk:
            p = self.assign_once("execute_from_disk_progress", self.glade.get_widget, "execute_from_disk_progress")
            p.hide()
            return
        self.read_one_query_started = False
        self.query_from_disk = False

    def on_eqfd_exclude_toggled(self, button):
        entry = self.glade.get_widget("eqfd_exclude_entry")
        entry.set_sensitive(button.get_active())

    def on_eqfd_limit_db_toggled(self, button):
        entry = self.glade.get_widget("eqfd_db_entry")
        entry.set_sensitive(button.get_active())

    def on_abort_execute_from_disk_clicked(self, button):
        self.window.hide()

    def read_one_query(self, fp, _start=None, count_lines=0, update_function=None, only_use_queries=False,
                       start_line=1):
        current_query = []
        self.read_one_query_started = True
        while self.read_one_query_started:
            gc.collect()
            if _start is None:
                while 1:
                    line = fp.readline()
                    if line == "":
                        if len(current_query) > 0:
                            return ' '.join(current_query), _start, count_lines
                        return None, _start, count_lines
                    if count_lines is not None:
                        count_lines += 1

                    if update_function is not None:
                        lb = fp.tell() - len(line)
                        update_function(False, lb)

                    if count_lines is not None and count_lines <= start_line:
                        #print count_lines
                        continue
                    first = line.lstrip("\r\n\t ")[0:15].lower()
                    if only_use_queries and first[0:3] != "use" and first != "create database":
                        continue
                    if line.lstrip(" \t")[0:2] != "--":
                        break
                        #print "skipping line", [line]
                self.last_query_line = line
                _start = 0
            else:
                line = self.last_query_line
            _start, end = read_query(line, _start)
            _next = line[end:end + 1]
            #print "next: '%s'" % next
            if _start is not None:
                #print "append query", [line[start:end]]
                current_query.append(line[_start:end])
            if _next == ";":
                return ''.join(current_query), end + 1, count_lines
            _start = None
        return None, None, None

    def assign_once(self, name, creator, *args):
        try:
            return self.created_once[name]
        except:
            obj = creator(*args)
            self.created_once[name] = obj
            return obj

if __name__ == '__main__':
    print 'Self run'

    instance = ExecuteQueryFromDisk(None)
    gtk.main()
