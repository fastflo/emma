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
import sys

version = "0.7"
new_instance = None
our_module = None

re_src_after_order_end = "(?:limit.*|procedure.*|for update.*|lock in share mode.*|[ \r\n\t]*$)"
re_src_after_order = "(?:[ \r\n\t]" + re_src_after_order_end + ")"
re_src_query_order = "(?is)(.*order[ \r\n\t]+by[ \r\n\t]+)(.*?)([ \r\n\t]*" + \
                     re_src_after_order_end + ")"

emmalib_file = os.path.abspath(__file__)
emma_path = os.path.dirname(emmalib_file)

if os.path.isdir("emmalib"):
    # svn dev env
    emma_share_path = "emmalib"
    icons_path = "icons"
    glade_path = emma_share_path
else:
    emma_share_path = os.path.join(sys.prefix, "share/emma/")
    icons_path = os.path.join(emma_share_path, "icons")
    glade_path = os.path.join(emma_share_path, "glade")

last_update = 0
