#!/usr/bin/env python
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

from glob import glob
from distutils.core import setup

from emmalib import version

icon_data = glob('icons/*.png')
glade_data = [
    'emmalib/emma.glade',
    'emmalib/plugins/table_editor/table_editor.glade',
    'emmalib/ConnectionWindow.glade'
]
other_data = ['changelog']

setup(name="emma",
      version=version,
      description="emma is the extendable mysql managing assistant",
      author="Florian Schmidt",
      author_email="flo@fastflo.de",
      url="http://emma.fastflo.de",
      scripts=['emma'],
      package_dir={'emmalib': 'emmalib'},
      packages=[
          'emmalib',
          'emmalib.plugins.table_editor',
          'emmalib.plugins.pretty_format',
          'emmalib.dialogs',
          'emmalib.providers',
          'emmalib.providers.mysql',
          'emmalib.providers.sqlite',
      ],
      data_files=[
          ("share/emma/icons", icon_data),
          ("share/emma/glade", glade_data),
          ("share/emma", other_data),
      ],
      license="GPL",
      long_description="""
Emma is a graphical toolkit for database developers and administrators
It provides dialogs to create or modify mysql databases, tables and 
associated indexes. it has a built-in syntax highlighting sql editor with 
table- and fieldname tab-completion and automatic sql statement formatting. 
the results of an executed query are displayed in a resultset where the record-
data can be edited by the user, if the sql statemant allows for it. the sql 
editor and resultset-view are grouped in tabs. results can be exported to csv 
files. multiple simultanios opend mysql connections are possible. 
Emma is the successor of yamysqlfront.
""",
      requires=['pyparsing'])

