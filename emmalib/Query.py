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

from Constants import *
from query_regular_expression import *


def read_query(query, _start=0):
    r = re.compile(r"""
        (?s)
        (
        ("(?:[^\\]|\\.)*?")|            # double quoted strings
        ('(?:[^\\]|\\.)*?')|            # single quoted strings
        (`(?:[^\\]|\\.)*?`)|            # backtick quoted strings
        (/\*.*?\*/)|                    # c-style comments
        (\#[^\n]*)|                     # shell-style comments
        (\--[^\n]*)|                        # sql-style comments
        ([^;])                          # everything but a semicolon
        )+
    """, re.VERBOSE)
    rw = re.compile("[ \r\n\t]+")

    m = rw.match(query, _start)
    if m:
        _start = m.end(0)

    match = r.match(query, _start)
    if not match:
        return None, len(query)
    return match.start(0), match.end(0)


def read_expression(query, _start=0, concat=True, update_function=None, update_offset=0, icount=0):
    r = query_regular_expression

    # print "read expr in", query
    match = r.search(query, _start)
    #if match: print match.groups()
    if not match:
        return None, None
    for i in range(1, match.lastindex + 1):
        if match.group(i):
            t = match.group(i)
            e = match.end(i)
            current_token = t
            if current_token[len(current_token) - 1] == "(":
                while 1:
                    icount += 1
                    if update_function is not None and icount >= 10:
                        icount = 0
                        update_function(False, update_offset + e)
                    # print "at", [query[e:e+15]], "..."
                    exp, end = read_expression(
                        query, e, False, update_function, update_offset, icount)
                    # print "got inner exp:", [exp]
                    if not exp:
                        break
                    e = end
                    if concat:
                        t += " " + exp
                    if exp == ")":
                        break

            return t, e
    print "should not happen!"
    return None, None


def get_order_from_query(query):
    current_order = []
    r = re.compile(re_src_query_order)
    # get current order by clause
    match = re.search(r, query)
    if not match:
        print "no order found in", [query]
        print "re:", [re_src_query_order]
        return current_order
    before, order, after = match.groups()
    order.lower()
    _start = 0
    ident = None
    while 1:
        item = []
        while 1:
            ident, end = read_expression(order[_start:])
            if not ident:
                break
            if ident == ",":
                break
            if ident[0] == "`":
                ident = ident[1:-1]
            item.append(ident)
            _start += end
        l = len(item)
        if l == 0:
            break
        elif l == 1:
            item.append(True)
        elif l == 2:
            if item[1].lower() == "asc":
                item[1] = True
            else:
                item[1] = False
        else:
            print "unknown order item:", item, "ignoring..."
            item = None
        if item:
            current_order.append(tuple(item))
        if not ident:
            break
        _start += 1  # comma
    return current_order


def is_query_appendable(query):
    pat = r'(?i)("(?:[^\\]|\\.)*?")|(\'(?:[^\\]|\\.)*?\')|(`(?:[^\\]|\\.)*?`)|(union)|(select[ \r\n\t]+(.*)[ \r\n\t]+from[ \r\n\t]+(.*))'
    r = re.compile(pat)
    _start = 0
    result = False
    while 1:
        result = re.search(r, query[_start:])
        if not result:
            return False
        _start += result.end()
        if result.group(4):
            return False  # union
        if result.group(5) and result.group(6) and result.group(7):
            break  # found select
    return result


# def search_query_end(self, text, _start):
#     try:
#         r = self.query_end_re
#     except:
#         r = self.query_end_re = re.compile(r'("(?:[^\\]|\\.)*?")|(\'(?:[^\\]|\\.)*?\')|(`(?:[^\\]|\\.)*?`)|(;)')
#     while 1:
#         result = re.search(r, text[_start:])
#         if not result:
#             return None
#
#         _start += result.end()
#         if result.group(4):
#             return _start

# def get_field_list(self, s):
#     # todo USE IT!
#     fields = []
#     _start = 0
#     ident = None
#     while 1:
#         item = []
#         while 1:
#             ident, end = self.read_expression(s[_start:])
#             if not ident:
#                 break
#             if ident == ",":
#                 break
#             if ident[0] == "`":
#                 ident = ident[1:-1]
#             item.append(ident)
#             _start += end
#         if len(item) == 1:
#             fields.append(item[0])
#         else:
#             fields.append(item)
#         if not ident:
#             break
#     print "found fields:", fields
#     return fields

