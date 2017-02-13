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

emma_instance = None
emma_registered_providers = []

if __name__ != 'emmalib':
    print "Don't run __init__.py - run ../emma instead"
    exit()

# package: python-gobject
try:
    import gobject
except:
    print "No gobject. Emma cannot start."
    exit(-1)

# package: python-gtk2
try:
    import gtk
    import gtk.gdk
    from gtk import keysyms
except:
    print "No gtk. Emma cannot start.", sys.exc_value
    exit(-1)

# package: python-glade2
try:
    import gtk.glade
except:
    print "No gtk.glade. Emma cannot start.", sys.exc_value
    exit(-1)

from OutputHandler import OutputHandler
from Constants import *
from Emma import Emma


def usage():
    
    print """usage: emma [-h|--help] [-d|--debug] [-l output_log [-f|--flush]]
 -h|--help     show this help message
 -d|--debug    output debug information on stdout
 -l|--log FILE append all output to a specified log file
 -f|--flush    flush {stdout,log} after each write
"""
    sys.exit(0)


def start(args):
    global emma_instance

    debug_output = False
    log_file = None
    log_flush = False

    skip = False
    for i, arg in enumerate(args):
        if skip:
            skip = False
            continue
        if arg == "-h" or arg == "--help":
            usage()
        elif arg == "-d" or arg == "--debug":
            debug_output = True
        elif arg == "-f" or arg == "--flush":
            log_flush = True
        elif arg == "-l" or arg == "--log":
            if i + 1 == len(args):
                usage()
            log_file = args[i + 1]
            skip = True
        else:
            usage()

    # this singleton will be accessible as sys.stdout!
    OutputHandler(debug_output, log_file, log_flush)

    emma_instance = Emma()
    emma_instance.start()
    gtk.main()

    return 0
