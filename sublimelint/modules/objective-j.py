# -*- coding: utf-8 -*-
# objective-j.py - Lint checking for Objective-J - given filename and contents of the code:
# It provides a list of line numbers to outline and offsets to highlight.
#
# This specific module is part of the SublimeLint project.
# It is a fork by Aparajita Fishman from the Kronuz fork of the original SublimeLint project,
# (c) 2011 Ryan Hileman and licensed under the MIT license.
# URL: http://bochs.info/
#
# The original copyright notices for this file/project follows:
#
# (c) 2005-2008 Divmod, Inc.
# See LICENSE file for details
#
# The LICENSE file is as follows:
#
# Copyright (c) 2005 Divmod, Inc., http://www.divmod.com/
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import os
import sublime
import sys

libs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs'))
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)

from capp_lint import LintChecker

language = 'Objective-J'
description =\
'''* view.run_command("lint", "Objective-J")
        Turns background linter off and runs the default Objective-J linter
        (capp_lint) on current view.
'''


def check(codeString, filename):
    return None


def run(code, view, filename='untitled'):
    lines = set()
    errorUnderlines = []  # leave this here for compatibility with original plugin
    errorMessages = {}
    warningUnderlines = []
    warningMessages = {}

    checker = LintChecker()
    checker.lint_text(code, filename)

    def addMessage(lineno, message, type):
        message = message.capitalize()
        errors = errorMessages if type == LintChecker.ERROR_TYPE_ILLEGAL else warningMessages

        if lineno in errors:
            errors[lineno].append(message)
        else:
            errors[lineno] = [message]

    def underlineRange(lineno, position, type):
        line = view.full_line(view.text_point(lineno, 0))
        position += line.begin()
        underlines = errorUnderlines if type == LintChecker.ERROR_TYPE_ILLEGAL else warningUnderlines
        underlines.append(sublime.Region(position))

    for error in checker.errors:
        lineno = error['lineNum'] - 1  # ST2 wants zero-based numbers
        lines.add(lineno)
        addMessage(lineno, error['message'], error['type'])

        for position in error.get('positions', []):
            underlineRange(lineno, position, error['type'])

    return lines, errorUnderlines, [], warningUnderlines, errorMessages, {}, warningMessages
