"""
MySQL Host class container
"""
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

import os
import re
import sys
import time
import traceback
import _mysql
import gobject

from MySqlDb import MySqlDb

# as of mysql 5.1:
# http://dev.mysql.com/doc/mysqld-version-reference/en/
# mysqld-version-reference-reservedwords-5-1.html
MYSQL_RESERVED_WORDS = """
ACCESSIBLE[a]   ADD     ALL
ALTER   ANALYZE     AND
AS  ASC     ASENSITIVE
BEFORE  BETWEEN     BIGINT
BINARY  BLOB    BOTH
BY  CALL    CASCADE
CASE    CHANGE  CHAR
CHARACTER   CHECK   COLLATE
COLUMN  CONDITION   CONNECTION[b]
CONSTRAINT  CONTINUE    CONVERT
CREATE  CROSS   CURRENT_DATE
CURRENT_TIME    CURRENT_TIMESTAMP   CURRENT_USER
CURSOR  DATABASE    DATABASES
DAY_HOUR    DAY_MICROSECOND     DAY_MINUTE
DAY_SECOND  DEC     DECIMAL
DECLARE     DEFAULT     DELAYED
DELETE  DESC    DESCRIBE
DETERMINISTIC   DISTINCT    DISTINCTROW
DIV     DOUBLE  DROP
DUAL    EACH    ELSE
ELSEIF  ENCLOSED    ESCAPED
EXISTS  EXIT    EXPLAIN
FALSE   FETCH   FLOAT
FLOAT4  FLOAT8  FOR
FORCE   FOREIGN     FROM
FULLTEXT    GOTO[c]     GRANT
GROUP   HAVING  HIGH_PRIORITY
HOUR_MICROSECOND    HOUR_MINUTE     HOUR_SECOND
IF  IGNORE  IN
INDEX   INFILE  INNER
INOUT   INSENSITIVE     INSERT
INT     INT1    INT2
INT3    INT4    INT8
INTEGER     INTERVAL    INTO
IS  ITERATE     JOIN
KEY     KEYS    KILL
LABEL[d]    LEADING     LEAVE
LEFT    LIKE    LIMIT
LINEAR  LINES   LOAD
LOCALTIME   LOCALTIMESTAMP  LOCK
LONG    LONGBLOB    LONGTEXT
LOOP    LOW_PRIORITY    MASTER_SSL_VERIFY_SERVER_CERT[e]
MATCH   MEDIUMBLOB  MEDIUMINT
MEDIUMTEXT  MIDDLEINT   MINUTE_MICROSECOND
MINUTE_SECOND   MOD     MODIFIES
NATURAL     NOT     NO_WRITE_TO_BINLOG
NULL    NUMERIC     ON
OPTIMIZE    OPTION  OPTIONALLY
OR  ORDER   OUT
OUTER   OUTFILE     PRECISION
PRIMARY     PROCEDURE   PURGE
RANGE   READ    READS
READ_ONLY[f]    READ_WRITE[g]   REAL
REFERENCES  REGEXP  RELEASE
RENAME  REPEAT  REPLACE
REQUIRE     RESTRICT    RETURN
REVOKE  RIGHT   RLIKE
SCHEMA  SCHEMAS     SECOND_MICROSECOND
SELECT  SENSITIVE   SEPARATOR
SET     SHOW    SMALLINT
SPATIAL     SPECIFIC    SQL
SQLEXCEPTION    SQLSTATE    SQLWARNING
SQL_BIG_RESULT  SQL_CALC_FOUND_ROWS     SQL_SMALL_RESULT
SSL     STARTING    STRAIGHT_JOIN
TABLE   TERMINATED  THEN
TINYBLOB    TINYINT     TINYTEXT
TO  TRAILING    TRIGGER
TRUE    UNDO    UNION
UNIQUE  UNLOCK  UNSIGNED
UPDATE  UPGRADE[h]  USAGE
USE     USING   UTC_DATE
UTC_TIME    UTC_TIMESTAMP   VALUES
VARBINARY   VARCHAR     VARCHARACTER
VARYING     WHEN    WHERE
WHILE   WITH    WRITE
XOR     YEAR_MONTH  ZEROFILL
ACCESSIBLE  LINEAR  MASTER_SSL_VERIFY_SERVER_CERT
RANGE   READ_ONLY   READ_WRITE
"""
MYSQL_RESERVED_WORDS = re.sub(r"\[.*?\]", "", MYSQL_RESERVED_WORDS.strip())
MYSQL_RESERVED_WORDS = re.split(r"[ \r\n\t]+", MYSQL_RESERVED_WORDS.lower())


class MySqlHost(object):
    """
    MySQL Host class
    """

    def __init__(self, *args):
        if len(args) == 2:
            # unpickle
            self.sql_log, self.msg_log = args
            # print "unpickle host!"
            db_name = ''
            if self.connected:
                db_name = self.current_db.name
                self.current_db = None
                # print "try to reconnect after unpickling!"
                self.connect()
                # print "resulting handle:", self.handle
            if self.connected:
                # print "unpickling databases!", self.handle
                for _, database in self.databases.iteritems():
                    database.__init__(self)
                self.use_db(db_name, True)
        else:
            self.sql_log, self.msg_log, self.name, self.host, self.port, self.user, self.password, \
                self.database, self.connect_timeout = args
            self.connected = False
            self.databases = {}  # name -> db_object
            self.current_db = None
            self.expanded = False
            self.handle = None

        self.processlist = None
        self.update_ui = None
        self.last_error = ""
        self.query_time = 0
        self.update_ui_args = None
        self.charset = "latin1"
        self.variables = dict()
        self.version = ""

    def __getstate__(self):
        statedict = dict(self.__dict__)
        for i in ["sql_log", "msg_log", "handle", "processlist", "update_ui", "update_ui_args"]:
            del statedict[i]
            # print "host will pickle:", d
        return statedict

    def get_connection_string(self):
        """
        :return: str
        """
        if self.port != "":
            output = "%s:%s" % (self.host, self.port)
        else:
            output = "%s" % self.host
        output += ",%s,%s,%s" % (self.user, self.password, self.database)
        return output

    def set_update_ui(self, update_ui, *args):
        """
        :param update_ui:
        :param args:
        """
        self.update_ui = update_ui
        self.update_ui_args = args

    def connect(self):
        """
        :return: None
        """
        conn = {
            "host": self.host,
            "user": self.user,
            "passwd": self.password,
            "connect_timeout": int(self.connect_timeout)
        }
        if self.port:
            conn["port"] = int(self.port)
        if self.database:
            conn["db"] = self.database

        try:
            self.handle = _mysql.connect(**conn)
        except:  # mysql_exceptions.OperationalError:
            self.connected = False
            msg = "%s: %s" % (sys.exc_type, sys.exc_value)
            # print msg
            if self.msg_log:
                self.msg_log(msg)
            return
        self.connected = True
        self.version = self.handle.get_server_info()
        # if self.is_at_least_version("4.1.0"):
        #     self.query("set names 'utf8'") # request utf8 encoded names and result!
        self.query("show variables")  # get server variables
        result = self.handle.store_result()
        self.variables = dict(result.fetch_row(0))
        if self.is_at_least_version("4.1.3"):
            self.charset = self.variables["character_set_server"]
        else:
            self.charset = "latin1"  # use config default_charset as fallback!
            # print "using default_charset %r for this database" % self.charset
            # print "server variables:"
            # import pprint
        # pprint.pprint(self.variables)
        self.refresh()
        if self.database:
            self.use_db(self.database)

    def is_at_least_version(self, requested):
        """
        :param requested: str
        :return: bool
        """
        requested = map(int, requested.split("."))
        real = self.version.replace("-", "_").split("_", 1)[0].split(".")
        real = map(lambda f: int(re.sub("[^0-9]", "", f)), real)
        for frst, scnd in zip(requested, real):
            if scnd > frst:
                return True
            if scnd < frst:
                return False
        return True

    def ping(self):
        """
        :return: bool
        """
        try:
            self.handle.ping()
            return True
        except:
            self.connected = False
            if self.msg_log:
                self.msg_log(sys.exc_value[1])
            return False

    def close(self):
        """
        Close connection
        """
        self.databases = {}
        self.processlist = None
        if self.handle:
            self.handle.close()
            self.handle = None
        self.current_db = None
        self.connected = False
        if self.update_ui:
            self.update_ui(self, *self.update_ui_args)

    def query(self, query, check_use=True, append_to_log=True, encoding=None):
        """
        :param query: str
        :param check_use: bool
        :param append_to_log: bool
        :param encoding: str
        :return:
        """
        if not self.handle:
            if self.msg_log:
                self.msg_log(
                    "Not connected! Can't execute %s, %s, %s" % (
                        query, str(self.handle), str(self)))
            return
        if append_to_log:
            if self.sql_log:
                self.sql_log(query)
        try:
            self.query_time = 0
            start = time.time()
            if encoding:
                query = query.encode(encoding, "ignore")
            # print "executing query (encoding: %s): %r" % (encoding, query)
            self.handle.query('SET NAMES utf8')
            self.handle.query(query)
            self.query_time = time.time() - start
        except:
            # print "error executing query:\n%s" % traceback.format_exc()
            try:
                self.last_error = sys.exc_value[1]
            except:
                self.last_error = str(sys.exc_value)
            message = sys.exc_value[1]
            # print "error:", [s]
            message = message.replace(
                "You have an error in your SQL syntax.  " +
                "Check the manual that corresponds to your MySQL "
                "server version for the right syntax to use near ",
                "MySQL syntax error at ")
            if self.msg_log:
                self.msg_log(message)
            else:
                # print message
                pass
            if sys.exc_value[0] == 2013:
                # lost connection
                self.close()
            return False

        if not check_use:
            return True
        match = re.match("(?is)^([ \r\n\t]*|#[^\n]*)*(use[ \r\n\t]*).*", query)
        if match:
            dbname = query[match.end(2):].strip("`; \t\r\n")
            # print "use db: '%s'" % dbname
            self.use_db(dbname, False)
            # reexecute to reset field_count and so on...
            self.handle.query(query)
        return True

    def query_dict(self, query, check_use=False, append_to_log=True, encoding=None):
        """
        :param query: str
        :param check_use: bool
        :param append_to_log: bool
        :param encoding: str
        :return: {}
        """
        if self.query(query, check_use, append_to_log, encoding):
            return result2hash(self.handle)

    def use_db(self, name, do_query=True):
        """
        :param name: str
        :param do_query: bool
        :return:
        """
        if self.current_db and name == self.current_db.name:
            return
        if do_query:
            self.query("use `%s`" % name, False)
        try:
            self.current_db = self.databases[name]
        except KeyError:
            # print "Warning: used an unknown database %r! please refresh host!\n%s" % (
            #     name, "".join(traceback.format_stack()))
            pass

    def select_database(self, database):
        """
        :param database: MySqlDb
        """
        self.use_db(database.name)

    def refresh(self):
        """
        Refresh host's databases list
        """
        self.query("show databases")
        result = self.handle.store_result()
        old = dict(self.databases)
        for row in result.fetch_row(0):
            if not row[0] in old:
                self.databases[row[0]] = MySqlDb(self, row[0])
            else:
                del old[row[0]]
        for database in old.keys():
            # print "remove database", database
            del self.databases[database]

    def refresh_processlist(self):
        """
        :return: None
        """
        if not self.query("show processlist"):
            return
        result = self.handle.store_result()
        self.processlist = (result.describe(), result.fetch_row(0))

    def insert_id(self):
        """
        :return: int
        """
        return self.handle.insert_id()

    def escape(self, strtoescape):
        """
        :param strtoescape: str
        :return: str
        """
        if strtoescape is None:
            return strtoescape
        return self.handle.escape_string(strtoescape)

    @staticmethod
    def escape_field(field):
        """
        :param field: str
        :return: str
        """
        if len(field) == 0:
            return ''
        # todo encode unicode strings here!
        # if already encoded:
        if "\x00" in field or "\0xff" in field:
            raise Exception("found invalid character in identifier %r!" % field)
        if field[-1] in " \r\t\n":
            raise Exception("identifiers should not end in space chars! %r" % field)
        if len(field) > 64:
            raise Exception("field name too long: %r / %d" % (field, len(field)))
        if field.lower() in MYSQL_RESERVED_WORDS or re.search("[` ]", field) or field.isdigit():
            retval = "`%s`" % field.replace("`", r"``")
        else:
            retval = field
        # print "escape field %r to %r" % (field, retval)
        return retval

    def escape_table(self, table):
        """
        :param table: str
        :return:
        """
        not_allowed = "".join(filter(lambda s: s, [
            os.curdir,
            os.pardir,
            os.sep,
            os.altsep,
            os.extsep,
            os.pathsep,
            os.linesep]))
        if set(table).intersection(set(not_allowed)):
            raise Exception(
                "before mysql 5.1.6 table names are not allowed "
                "to contain one of these chars: %r %r" % (not_allowed, table)
            )
        if len(table) > 64:
            raise Exception("table name too long: %r / %d" % (table, len(table)))
        return self.escape_field(table)

    def get_escaped_name(self):
        """
        :@return : str
        """
        return self.name.replace('&', '&amp;').replace('<', '&lt;')


def result2hash(host, cols=True):
    """
    :param host:
    :param cols:
    :return:
    """
    res = host.store_result()
    ret = {"rows": []}
    if res is not None:
        _cols = []
        _types = []
        for host in res.describe():
            _cols.append(host[0])
            _types.append(mysql2gobject(host[1]))
        for row in res.fetch_row(0):
            ret['rows'].append(dict(zip(_cols, row)))
        if cols:
            ret['cols'] = _cols
            ret['types'] = _types
    return ret


def mysql2gobject(typecode):
    """
    :param typecode: int
    :return: type
    """
    array = {
        16: gobject.TYPE_INT,
        252: gobject.TYPE_STRING,
        1: gobject.TYPE_STRING,
        10: gobject.TYPE_STRING,
        12: gobject.TYPE_STRING,
        0: gobject.TYPE_FLOAT,
        5: gobject.TYPE_FLOAT,
        247: gobject.TYPE_STRING,
        4: gobject.TYPE_FLOAT,
        255: gobject.TYPE_STRING,
        9: gobject.TYPE_LONG,
        3: gobject.TYPE_LONG,
        251: gobject.TYPE_STRING,
        8: gobject.TYPE_LONG,
        250: gobject.TYPE_STRING,
        14: gobject.TYPE_STRING,
        246: gobject.TYPE_FLOAT,
        6: gobject.TYPE_STRING,
        248: gobject.TYPE_STRING,
        2: gobject.TYPE_INT,
        254: gobject.TYPE_STRING,
        11: gobject.TYPE_STRING,
        7: gobject.TYPE_STRING,
        249: gobject.TYPE_STRING,
        253: gobject.TYPE_STRING,
        15: gobject.TYPE_STRING,
        13: gobject.TYPE_STRING
    }
    return array[typecode]


def mysql2py(typecode):
    """
    :param typecode: int
    :return: type
    """
    d = {
        16: int,
        252: str,
        1: str,
        10: str,
        12: str,
        0: float,
        5: float,
        247: str,
        4: float,
        255: str,
        9: long,
        3: long,
        251: str,
        8: long,
        250: str,
        14: str,
        246: float,
        6: str,
        248: str,
        2: int,
        254: str,
        11: str,
        7: str,
        249: str,
        253: str,
        15: str,
        13: str
    }
    return d[typecode]
