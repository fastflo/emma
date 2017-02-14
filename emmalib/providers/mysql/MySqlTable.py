"""
MySQL Table class container
"""
# -*- coding: utf-8 -*-
# emma
#
# Copyright (C) 2006 Florian Schmidt (flo@fastflo.de)
# 2014 Nickolay Karnaukhov (mr.electronick@gmail.com)
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

from emmalib import emma_instance
from emmalib.dialogs import confirm
from emmalib.EventsManager import EventsManager
from emmalib.providers.mysql.MySqlField import MySqlField
from emmalib.providers.mysql.MySqlIndex import MySqlIndex
from emmalib.providers.mysql.widgets import TableFields
from emmalib.providers.mysql.widgets import TableIndexes
from emmalib.providers.mysql.widgets import TableProperties
from emmalib.providers.mysql.widgets import TableToolbar


class MySqlTable(EventsManager):
    """
    :@param db
    :@param props
    :@param pros_description
    """

    def __init__(self, db, props, props_description):
        super(MySqlTable, self).__init__()
        self.handle = db.handle
        self.host = db.host
        self.db = db
        self.name = props[0]
        self.fields = []
        self.indexes = []
        self.expanded = False
        self.create_table = ""
        self.engine = props[1]
        self.comment = props[17]
        self.is_table = False
        self.is_view = False
        self.props = props

        self.props_dict = dict(zip(map(lambda v: v[0], props_description), props))
        self.props_description = props_description

        if self.engine:
            self.is_table = True
        else:
            self.is_view = True

    def refresh(self, refresh_props=True):
        """
        :param refresh_props: bool
        """
        self.db.host.select_database(self.db)
        if refresh_props:
            self.refresh_properties()
        self.refresh_fields()
        self.refresh_indexes()
        self.trigger('changed', self)

    def refresh_properties(self):
        """
        Refresh table properties
        """
        _qeury = "show table status like '%s'" % self.name
        self.host.query(_qeury)
        result = self.handle.store_result()
        rows = result.fetch_row(0)
        self.props = rows[0]
        self.props_dict = dict(zip(map(lambda v: v[0], result.describe()), rows[0]))
        self.name = self.props[0]

    def refresh_fields(self):
        """
        :return: None
        """
        self.fields = []
        res = self.host.query_dict("show full columns from `%s`" % self.host.escape_table(self.name))
        if not res:
            return
        for row in res['rows']:
            self.fields.append(MySqlField(row))

    def refresh_indexes(self):
        """
        :return: None
        """
        self.indexes = []
        res = self.host.query_dict('SHOW INDEX FROM `%s`' % self.host.escape_table(self.name))
        if not res:
            return
        for row in res['rows']:
            self.indexes.append(MySqlIndex(row))

    def get_create_table(self):
        """
        :return: str
        """
        self.db.host.select_database(self.db)
        self.host.query("show create table `%s`" % self.host.escape_table(self.name))
        result = self.handle.store_result()
        if not result:
            # print "can't get create table for %s at %s and %s" % (self.name, self, self.handle)
            return ""
        result = result.fetch_row(0)
        self.create_table = result[0][1]
        return self.create_table

    def get_tree_row(self, field_name):
        """
        :param field_name: str
        :return:
        """
        return (self.fields[field_name][0], self.fields[field_name][1]),

    def get_all_records(self):
        """
        :return: dict
        """
        return self.host.query_dict('SELECT * FROM `%s`' % self.host.escape_table(self.name))

    #
    # ALTER TABLE
    #

    def rename(self, new_name):
        """
        :param new_name: str
        :return: bool
        """
        oldname = self.host.escape_table(self.name)
        newname = self.host.escape_table(new_name)
        query = 'RENAME TABLE `%s` TO `%s`' % (oldname, newname)
        if self.host.query(query, False, True):
            self.db.tables[new_name] = self
            del self.db.tables[self.name]
            self.name = new_name
            self.refresh_properties()
            self.trigger('changed', self)
            return True

    def alter_engine(self, new_engine):
        """
        :param new_engine:
        """
        if self.host.query('ALTER TABLE `%s` ENGINE=`%s`' % (
                self.host.escape_table(self.name),
                new_engine.upper()
        )):
            self.refresh_properties()
            self.trigger('changed', self)

    def alter_row_format(self, new_row_format):
        """
        :param new_row_format:
        """
        if self.host.query('ALTER TABLE `%s` ROW_FORMAT=`%s`' % (
                self.host.escape_table(self.name),
                new_row_format.upper()
        )):
            self.refresh_properties()
            self.trigger('changed', self)

    def alter_comment(self, new_comment):
        """
        :param new_comment:
        """
        if self.host.query("ALTER TABLE `%s` COMMENT='%s'" % (
                self.host.escape_table(self.name),
                new_comment
        )):
            self.refresh_properties()
            self.trigger('changed', self)

    def alter_auto_increment(self, new_ai):
        """
        :param new_ai:
        """
        if self.host.query("ALTER TABLE `%s` AUTO_INCREMENT=%s" % (
                self.host.escape_table(self.name),
                new_ai
        )):
            self.refresh_properties()
            self.trigger('changed', self)

    def alter_collation(self, charset, collation):
        """
        :param charset:
        :param collation:
        """
        if self.host.query(
                        "ALTER TABLE `%s` DEFAULT CHARACTER SET %s COLLATE %s" % (
                            self.host.escape_table(self.name),
                            charset, collation
                )):
            self.refresh_properties()
            self.trigger('changed', self)

    def drop_field(self, field_name):
        """
        :param field_name:
        """
        if self.host.query("ALTER TABLE `%s` DROP `%s`" % (self.host.escape_table(self.name),
                                                           field_name)):
            self.refresh()
            self.trigger('changed', self)

    #
    #   WIDGETS
    #

    def get_table_properties_widget(self):
        """
        :return:
        """
        if self.is_table:
            return TableProperties(self)
        else:
            return False

    def get_table_fields_widget(self):
        """
        :return:
        """
        if self.is_table:
            return TableFields(self)
        else:
            return False

    def get_table_indexes_widget(self):
        """
        :return:
        """
        if self.is_table:
            return TableIndexes(self)
        else:
            return False

    def get_table_toolbar(self, tab_table):
        """
        :param tab_table:
        :return:
        """
        if self.is_table:
            toolbar = TableToolbar(tab_table)
            toolbar.refresh.connect('clicked', self.on_toolbar_refresh_table)
            toolbar.drop.connect('clicked', self.on_toolbar_drop_table)
            toolbar.truncate.connect('clicked', self.on_toolbar_truncate_table)
            return toolbar
        else:
            return False

    def get_table_status_string(self):
        """
        :return:
        """
        return 'Engine: %s, Rows: %s, Collation: %s, Comment: %s' % \
               (self.props[1], self.props[4], self.props[14], self.props[17])

    def on_toolbar_refresh_table(self, _):
        """
        :param _:
        """
        self.refresh(True)

    def on_toolbar_drop_table(self, _):
        """
        :param _:
        :return:
        """
        if not confirm(
                "Drop table",
                "do you really want to DROP the <b>%s</b> table in database "
                "<b>%s</b> on <b>%s</b>?" % (
                        self.get_escaped_name(),
                        self.db.get_escaped_name(),
                        self.db.host.get_escaped_name()
                ),
                None):
            return
        if self.db.query("drop table `%s`" % self.name):
            if emma_instance:
                self.trigger('changed', self)
                self.trigger('dropped', self)

    def on_toolbar_truncate_table(self, _):
        """
        :param _:
        :return:
        """
        if not confirm(
                "Truncate table",
                "Do You really want to TRUNCATE the <b>%s</b> table in database "
                "<b>%s</b> on <b>%s</b>?" % (
                        self.get_escaped_name(),
                        self.db.get_escaped_name(),
                        self.db.host.get_escaped_name()
                ),
                None):
            return
        if self.db.query("truncate table `%s`" % self.name):
            self.trigger('changed', self)

    def get_escaped_name(self):
        """
        :@return : str
        """
        return self.name.replace('&', '&amp;').replace('<', '&lt;')
