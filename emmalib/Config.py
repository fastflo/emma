import os
import gtk
import sys
import dialogs


class Config:
    def __init__(self, emma=None):
        self.emma = emma
        self.unpickled = False
        filename = False
        for i in ["HOME", "USERPROFILE"]:
            filename = os.getenv(i)
            if filename:
                break
        if not filename:
            filename = "."
        filename += "/.emma"
        print filename
        if os.path.isfile(filename):
            print "detected emma config file %r. converting to directory" % filename
            temp_dir = filename + "_temp"
            os.mkdir(temp_dir)
            os.rename(filename, os.path.join(temp_dir, "emmarc"))
            os.rename(temp_dir, filename)
        self.supported_db_encodings = {}
        self.codings = {}
        self.stored_orders = {}
        self.config_path = filename
        self.config_file = "emmarc"
        self.config = {
            "null_color": "#00eeaa",
            "autorefresh_interval_table": "300",
            "column_sort_use_newline": "true",
            "query_text_font": "Monospace 8",
            "query_text_wrap": "false",
            "query_result_font": "Monospace 8",
            "query_log_max_entry_length": "1024",
            "result_view_column_width_min": "70",
            "result_view_column_width_max": "300",
            "result_view_column_resizable": "false",
            "result_view_column_sort_timeout": "750",
            "syntax_highlight_keywords": "lock, unlock, tables, kill, truncate table, alter table, host, database, field, comment, show table status, show index, add index, drop index, add primary key, add unique, drop primary key, show create table, values, insert into, into, select, show databases, show tables, show processlist, show tables, from, where, order by, group by, limit, left, join, right, inner, after, alter, as, asc, before, begin, case, column, change column, commit, create table, default, delete, desc, describe, distinct, drop, table, first, grant, having, insert, interval, insert into, limit, null, order, primary key, primary, auto_increment, rollback, set, start, temporary, union, unique, update, create database, use, key, type, uniqe key, on, type, not, unsigned",
            "syntax_highlight_functions": "date_format, now, floor, rand, hour, if, minute, month, right, year, isnull",
            "syntax_highlight_functions": "abs, acos, adddate, addtime, aes_decrypt, aes_encrypt, ascii, asin, atan, benchmark, bin, bit_length, ceil, ceiling, char, character_length, char_length, charset, coercibility, collation, compress, concat, concat_ws, connection_id, conv, convert_tz, cos, cot, crypt, curdate, current_date, current_time, current_timestamp, current_user, curtime, database, date, date_add, datediff, date_format, date_sub, day, dayname, dayofmonth, dayofweek, dayofyear, decode, default, degrees, des_decrypt, des_encrypt, elt, encode, encrypt, exp, export_set, extract, field, find_in_set, floor, format, found_rows, from_days, from_unixtime, get_format, get_lock, hex, hour, if, ifnull, inet_aton, inet_ntoa, insert, instr, is_free_lock, is_used_lock, last_day, last_insert_id, lcase, left, length, ln, load_file, localtime, localtimestamp, locate, log, lower, lpad, ltrim, makedate, make_set, maketime, master_pos_wait, microsecond, mid, minute, mod, month, monthname, mysql_insert_id, now, nullif, oct, octet_length, old_password, ord, order by rand, password, period_add, period_diff, pi, position, pow, power, quarter, quote, radians, rand, release_lock, repeat, replace, reverse, right, round, row_count, rpad, rtrim, schema, second, sec_to_time, session_user, sha, sign, sin, sleep, soundex, space, sqrt, str_to_date, subdate, substr, substring, substring_index, subtime, sysdate, system_user, tan, time, timediff, time_format, timestamp, timestampadd, timestampdiff, time_to_sec, to_days, trim, truncate, ucase, uncompress, uncompressed_length, unhex, unix_timestamp, upper, user, utc_date, utc_time, utc_timestamp, uuid, version, week, weekday, weekofyear, year, yearweek",
            "syntax_highlight_datatypes": "binary, bit, blob, boolean, char, character, dec, decimal, double, float, int, integer, numeric, smallint, timestamp, varchar, datetime, text, mediumint, bigint, tinyint, date",
            "syntax_highlight_operators": "not, and, or, like, \\<, \\>",
            "syntax_highlight_fg_keyword": "#00007F",
            "syntax_highlight_fg_function": "darkblue",
            "syntax_highlight_fg_datatype": "#AA00AA",
            "syntax_highlight_fg_operator": "#0000aa",
            "syntax_highlight_fg_double-quoted-string": "#7F007F",
            "syntax_highlight_fg_single-quoted-string": "#9F007F",
            "syntax_highlight_fg_backtick-quoted-string": "#BF007F",
            "syntax_highlight_fg_number": "#007F7F",
            "syntax_highlight_fg_comment": "#007F00",
            "syntax_highlight_fg_error": "red",
            "pretty_print_uppercase_keywords": "false",
            "pretty_print_uppercase_operators": "false",
            "template1_last 150 records": "select * from $table$ order by $primary_key$ desc limit 150",
            "template2_500 records in fs-order": "select * from $table$ limit 500",
            "template3_quick filter 500": "select * from $table$ where $field_conditions$ limit 500",
            "copy_record_as_csv_delim": ",",
            "save_result_as_csv_delim": ",",
            "save_result_as_csv_line_delim": "\\n",
            "ping_connection_interval": "300",
            "ask_execute_query_from_disk_min_size": "1024000",
            "connect_timeout": "7",
            "db_encoding": "latin1",
            "supported_db_encodings":
                "latin1 (iso8859-1, cp819); "
                "latin2 (iso8859-2); "
                "iso8859_15 (iso8859-15); "
                "utf8;"
                "utf7;"
                "utf16; "
                "ascii (646);"
                "cp437 (IBM437);"
                "cp500 (EBCDIC-CP-BE); "
                "cp850 (IBM850); "
                "cp1140 (ibm1140); "
                "cp1252 (windows-1252); "
                "mac_latin2; mac_roman"
        }

    def load(self, unpickled=False):
        self.unpickled = unpickled
        filename = os.path.join(self.config_path, self.config_file)
        # todo get_charset(self.config["db_codeset"]);
        # printf("system charset: '%s'\n", self.config["db_codeset"].c_str());
        # syntax_highlight_functions: grep -E -e "^[ \\t]+<code class=\"literal[^>]*>[^\(<90-9]+\(" mysql_fun.html fun*.html | sed -r -e "s/^[^<]*<code[^>]+>//" -e "s/\(.*$/,/" | tr "[:upper:]" "[:lower:]" | sort | uniq | xargs echo

        if not os.path.exists(filename):
            print "no config file %r found. using defaults." % filename
            self.config["connection_localhost"] = "localhost,root,,"
        else:
            try:
                fp = file(filename, "r")
                line_no = 0
                for line in fp:
                    line_no += 1
                    line.lstrip(" \t\r\n")
                    if not line: continue
                    if line[0] == '#': continue
                    varval = line.split("=", 1)
                    name, value = map(lambda a: a.strip("\r\n \t"), varval)
                    value = varval[1].strip("\r\n \t")
                    self.config[name] = value
                    #setattr(self, "cfg_%s" % name, value)
                fp.close()
            except:
                print "could not load config file %r: %s" % (filename, sys.exc_value)
                self.config["connection_localhost"] = "localhost,root,,"

        # split supported encodings in list
        self.supported_db_encodings = map(lambda e: e.strip(), self.config["supported_db_encodings"].split(";"))

        for index, coding in enumerate(self.supported_db_encodings):
            try:
                _c, description = coding.split(" ", 1)
            except:
                _c = coding
                description = ""
            self.codings[_c] = (index, description)

        try:
            coding = self.config["db_encoding"]
            index = self.codings[coding][0]
        except:
            index = 0
            coding, description = self.supported_db_encodings[index].split(" ", 1)
            self.config["db_encoding"] = coding

        # stored orders
        for name in self.config.keys():
            if not name.startswith("stored_order_db_"):
                continue
            words = name.split("_")
            db = words[3]
            table = words[5]
            if not db in self.stored_orders:
                self.stored_orders[db] = {}
            self.stored_orders[db][table] = eval(self.config[name])

        if not unpickled:
            return

    def get(self, name):
        return self.config[name]

    def get_bool(self, name):
        value = self.get(name).lower()
        if value == "yes":
            return True
        if value == "y":
            return True
        if value == "1":
            return True
        if value == "true":
            return True
        if value == "t":
            return True
        return False

    def save(self):
        self.emma.add_msg_log('config.save')
        if not os.path.exists(self.config_path):
            print "try to create config path %r" % self.config_path
            try:
                os.mkdir(self.config_path)
            except:
                dialogs.show_message("save config file",
                                     "could create config directory %r: %s" % (self.config_path, sys.exc_value))
                return

        filename = os.path.join(self.config_path, self.config_file)
        try:
            fp = file(filename, "w")
        except:
            dialogs.show_message("save config file", "could not open %s for writing: %s" % (filename, sys.exc_value))
            return

        keys = self.config.keys()
        keys.sort()
        for name in keys:
            if name.startswith("connection_"):
                continue
            value = self.config[name]
            fp.write("%s=%s\n" % (name, value))

        if self.emma:
            itr = self.emma.connections_model.get_iter_root()
            while itr:
                host = self.emma.connections_model.get_value(itr, 0)
                _str_to_write = "connection_%s=%s\n" % (host.name, host.get_connection_string())
                fp.write(_str_to_write)
                itr = self.emma.connections_model.iter_next(itr)
            fp.close()

# if __name__ != 'main':
#     c = Config()
#     c.load()
#     c.save()
#     print c.__dict__

