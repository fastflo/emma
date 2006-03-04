#!/usr/bin/env python
import os
import os.path
import sys
from glob import glob
from distutils.core import setup

import emma

setup(name="emma",
      version=emma.version,
      description="emma is the extendable mysql managing assistant",
      author="Florian Schmidt",
      author_email="fastflo@users.sourceforge.net",
      url="http://emma.sourceforge.net",
      scripts=['run_emma.py'],
      ##package_dir={'': 'modules'},
      packages=['emma', "."],
      data_files=[(emma.icons_path, glob(os.path.join("icons", "*.png"))),
                  (emma.emma_path, glob('emma.glade'))
                  ],
      license="GPL",
      extra_path='emma',
      long_description="""
Emma is a graphical toolkit for MySQL database developers and administrators
It provides dialogs to create or modify mysql databases, tables and 
associated indexes. it has a built-in syntax highlighting sql editor with 
table- and fieldname tab-completion and automatic sql statement formatting. 
the results of an executed query are displayed in a resultset where the record-
data can be edited by the user, if the sql statemant allows for it. the sql 
editor and resultset-view are grouped in tabs. results can be exported to csv 
files. multiple simultanios opend mysql connections are possible. 
Emma is the successor of yamysqlfront.
"""
      )

