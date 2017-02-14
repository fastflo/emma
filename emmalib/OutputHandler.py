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

import sys
import datetime


class OutputHandler(object):
    """
    Emma's output handler
    """
    def __init__(self, print_stdout=False, log_file=None, log_flush=False):
        self.stdout = sys.stdout
        self.print_stdout = print_stdout
        self.log_flush = log_flush
        sys.stdout = self
        if log_file:
            self.log_fp = file(log_file, "a+")
        else:
            self.log_fp = None
        self.debug = print_stdout or log_file

    def write(self, s):
        """
        @param s: str
        @return:
        """
        if self.print_stdout:
            self.stdout.write(s)
            if self.log_flush:
                self.stdout.flush()
        if self.log_fp:
            s = s.strip("\r\n")
            if not s:
                # do not write empty lines to logfile
                return
            timestamp = str(datetime.datetime.now())[0:22]
            self.log_fp.write(
                "%s %s\n" % (timestamp, s.replace("\n", "\n " + (" " * len(timestamp)))))
            if self.log_flush:
                self.log_fp.flush()
