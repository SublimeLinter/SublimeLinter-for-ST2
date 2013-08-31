# -*- coding: utf-8 -*-
# python.py - Lint checking for Python - given filename and contents of the code:
# It provides a list of line numbers to outline and offsets to highlight.
#
# This specific module is part of the SublimeLinter project.
# It is a fork by Andre Roberge from the original SublimeLint project,
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

# TODO:
# * fix regex for variable names inside strings (quotes)
import os
import pickle
import re
import subprocess

import pep8
import pyflakes.checker as pyflakes
from python_extra import Pep8Error, Pep8Warning, OffsetError

from base_linter import BaseLinter

pyflakes.messages.Message.__str__ = lambda self: self.message % self.message_args

CONFIG = {
    'language': 'Python'
}


class Linter(BaseLinter):
    def pyflakes_check(self, code, filename, ignore=None):
        args = '/usr/local/Frameworks/Python.framework/Versions/2.7/bin/python'

        process = subprocess.Popen(args,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   startupinfo=self.get_startupinfo())

        escaped = code.replace('\\', '\\\\').replace('"', '\\"')

        relative = os.path.join(__file__, '../../..')
        linter_folder = os.path.abspath(relative)

        to_send = """
import pickle
import sys

linter_folder = '"""+linter_folder+"""'
sys.path.append(linter_folder)
sys.path.append(linter_folder+'/sublimelinter/modules/libs')

from sublimelinter.modules.python_extra import PythonLintError, OffsetError, external_pyflakes_check
import pyflakes.checker as pyflakes

code = \"\"\"""" + escaped + """\"\"\"
filename = '""" + filename + """'

result = external_pyflakes_check(code, filename)
# print result
print pickle.dumps(result)
"""
        process.stdin.write(to_send)
        result = process.communicate()[0]

        w = pickle.loads(result)
        return w

    def pep8_check(self, code, filename, ignore=None):
        messages = []
        _lines = code.split('\n')

        if _lines:
            class SublimeLinterReport(pep8.BaseReport):
                def error(self, line_number, offset, text, check):
                    """Report an error, according to options."""
                    code = text[:4]
                    message = text[5:]

                    if self._ignore_code(code):
                        return
                    if code in self.counters:
                        self.counters[code] += 1
                    else:
                        self.counters[code] = 1
                        self.messages[code] = message

                    # Don't care about expected errors or warnings
                    if code in self.expected:
                        return

                    self.file_errors += 1
                    self.total_errors += 1

                    if code.startswith('E'):
                        messages.append(Pep8Error(filename, line_number, offset, code, message))
                    else:
                        messages.append(Pep8Warning(filename, line_number, offset, code, message))

                    return code

            _ignore = ignore + pep8.DEFAULT_IGNORE.split(',')

            options = pep8.StyleGuide(reporter=SublimeLinterReport, ignore=_ignore).options
            options.max_line_length = pep8.MAX_LINE_LENGTH

            good_lines = [l + '\n' for l in _lines]
            good_lines[-1] = good_lines[-1].rstrip('\n')

            if not good_lines[-1]:
                good_lines = good_lines[:-1]

            try:
                pep8.Checker(filename, good_lines, options).check_all()
            except Exception, e:
                print "An exception occured when running pep8 checker: %s" % e

        return messages

    def built_in_check(self, view, code, filename):
        errors = []

        if view.settings().get("pep8", True):
            errors.extend(self.pep8_check(code, filename, ignore=view.settings().get('pep8_ignore', [])))

        pyflakes_ignore = view.settings().get('pyflakes_ignore', None)
        pyflakes_disabled = view.settings().get('pyflakes_disabled', False)

        if not pyflakes_disabled:
            errors.extend(self.pyflakes_check(code, filename, pyflakes_ignore))

        return errors

    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):

        def underline_word(lineno, word, underlines):
            regex = r'((and|or|not|if|elif|while|in)\s+|[+\-*^%%<>=\(\{{])*\s*(?P<underline>[\w\.]*{0}[\w]*)'.format(re.escape(word))
            self.underline_regex(view, lineno, regex, lines, underlines, word)

        def underline_import(lineno, word, underlines):
            linematch = '(from\s+[\w_\.]+\s+)?import\s+(?P<match>[^#;]+)'
            regex = '(^|\s+|,\s*|as\s+)(?P<underline>[\w]*{0}[\w]*)'.format(re.escape(word))
            self.underline_regex(view, lineno, regex, lines, underlines, word, linematch)

        def underline_for_var(lineno, word, underlines):
            regex = 'for\s+(?P<underline>[\w]*{0}[\w*])'.format(re.escape(word))
            self.underline_regex(view, lineno, regex, lines, underlines, word)

        def underline_duplicate_argument(lineno, word, underlines):
            regex = 'def [\w_]+\(.*?(?P<underline>[\w]*{0}[\w]*)'.format(re.escape(word))
            self.underline_regex(view, lineno, regex, lines, underlines, word)

        errors.sort(lambda a, b: cmp(a.lineno, b.lineno))
        ignoreImportStar = view.settings().get('pyflakes_ignore_import_*', True)

        for error in errors:
            try:
                error_level = error.level
            except AttributeError:
                error_level = 'W'
            if error_level == 'E':
                messages = errorMessages
                underlines = errorUnderlines
            elif error_level == 'V':
                messages = violationMessages
                underlines = violationUnderlines
            elif error_level == 'W':
                messages = warningMessages
                underlines = warningUnderlines

            if isinstance(error, pyflakes.messages.ImportStarUsed) and ignoreImportStar:
                continue

            self.add_message(error.lineno, lines, str(error), messages)

            if isinstance(error, (Pep8Error, Pep8Warning, OffsetError)):
                self.underline_range(view, error.lineno, error.offset, underlines)

            elif isinstance(error, (pyflakes.messages.RedefinedWhileUnused,
                                    pyflakes.messages.UndefinedName,
                                    pyflakes.messages.UndefinedExport,
                                    pyflakes.messages.UndefinedLocal,
                                    pyflakes.messages.Redefined,
                                    pyflakes.messages.UnusedVariable)):
                underline_word(error.lineno, error.message, underlines)

            elif isinstance(error, pyflakes.messages.ImportShadowedByLoopVar):
                underline_for_var(error.lineno, error.message, underlines)

            elif isinstance(error, pyflakes.messages.UnusedImport):
                underline_import(error.lineno, error.message, underlines)

            elif isinstance(error, pyflakes.messages.ImportStarUsed):
                underline_import(error.lineno, '*', underlines)

            elif isinstance(error, pyflakes.messages.DuplicateArgument):
                underline_duplicate_argument(error.lineno, error.message, underlines)

            elif isinstance(error, pyflakes.messages.LateFutureImport):
                pass

            else:
                print 'Oops, we missed an error type!', type(error)
