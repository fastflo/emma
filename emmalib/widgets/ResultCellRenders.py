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


def render_mysql_string(column, cell, model, _iter, _id):
    o = model.get_value(_iter, _id)
    if not o is None:
        cell.set_property("foreground", None)
        cell.set_property("background", None)
        cell.set_property("text", o)
        cell.set_property("editable", True)
        # if len(o) < 256:
        #     cell.set_property("text", o)
        #     cell.set_property("editable", True)
        # else:
        #     cell.set_property("text", o[0:256] + "...")
        #     cell.set_property("editable", False)
    else:
        # cell.set_property("background", self.config.get("null_color"))
        cell.set_property("foreground", "#888888")
        cell.set_property("text", "<null>")
        cell.set_property("editable", True)