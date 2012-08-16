# -*- coding: utf-8 -*-
# erlang.py - sublimelint package for checking Erlang files
#
# Inpsired by the excellent erlang-flymake.el that ships with Erlang/OTP:
# https://github.com/erlang/otp/blob/maint/lib/tools/emacs/erlang-flymake.el
#

#
# Copyright (c) 2012 Seth Chisamore, http://seth.chisamore.com
# See LICENSE file for details
#
# The LICENSE file is as follows:
#
# Copyright (c) 2012 Seth Chisamore, http://seth.chisamore.com
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

#
# Projects are assumed to follow a variants of the Erlang OTP directory
# structure standard:
#
#       .                                 .
#       ├── deps/                         ├── apps/
#       │   ├── dep1/                     │   ├── app1/
#       │   └── dep2/                     │   └── app2/
#       ├── ebin/                         │       ├── ebin/
#       ├── include/                      │       ├── include/
#       ├── priv/                         │       ├── priv/
#       ├── src/                          │       ├── src/
#       ├── test/                         │       ├── test/
#       └── rebar.config                  │       └── rebar.config
#                                         ├── deps/
#                                         │   ├── dep1/
#                                         │   └── dep2/
#                                         ├── rel/
#                                         └── rebar.config

#
# Rebar conventions are also fully supported, including resolution of the
# include and ebin directories of a project's dependencies in the Rebar deps
# dir.
#

import re
import os.path
import glob

from base_linter import BaseLinter, INPUT_METHOD_TEMP_FILE

CONFIG = {
    'language': 'Erlang',
    'executable': 'erlc',
    'input_method': INPUT_METHOD_TEMP_FILE
}

class Linter(BaseLinter):

    DEFAULT_COMPILER_OPTS = [
        "+warn_obsolete_guard",
        "+warn_unused_import",
        "+warn_shadow_vars",
        "+warn_export_vars",
        "+strong_validation",
        "+report"
    ]

    DEFAULT_INCLUDE_DIRS = [
        "include",
        "src",
        "lib"
    ]

    DEFAULT_CODE_PATH_DIRS = [
        "ebin"
    ]

    DEFAULT_DEPENDENCY_DIRS = [
        "apps",
        "deps",
        "lib"
    ]

    LINE_RE = re.compile(r'^.+:(?P<line>\d+):\s(?P<warning>Warning:\s)?(?P<message>.+)$')

    def get_lint_args(self, view, code, filename):
        src_dir = os.path.dirname(view.file_name())
        project_dir = os.path.dirname(src_dir)

        result = ["-v"]

        for compiler_opt in self.DEFAULT_COMPILER_OPTS:
            result.append(compiler_opt)

        for include_dir in self.DEFAULT_INCLUDE_DIRS:
            include_path = self.find_file_or_dir(include_dir, view)
            if include_path:
                result.extend(["-I", include_path])

        for code_path_dir in self.DEFAULT_CODE_PATH_DIRS:
            code_path = self.find_file_or_dir(code_path_dir, view)
            if code_path:
                result.extend(["-pa", code_path])

        # Search for addtional include and code paths in depedencies
        for dependecy_root_dir in self.DEFAULT_DEPENDENCY_DIRS:
            dependecy_root = self.find_file_or_dir(dependecy_root_dir, view)
            if dependecy_root:
                result.extend(["-I", dependecy_root])
                for code_path_dir in glob.glob(os.path.join(dependecy_root, "*", "ebin")):
                    result.extend(["-pa", os.path.abspath(code_path_dir)])

        result.append(filename)

        return result

    #
    # Example output from 'erlc':
    #
    #       src/foo.erl:71: syntax error before: from_json
    #       src/foo.erl:35: function from_json/2 undefined
    #       src/foo.erl:64: Warning: variable 'A' is unused
    #
    def parse_errors(self, view, errors, lines, errorUnderlines,
                     violationUnderlines, warningUnderlines, errorMessages,
                     violationMessages, warningMessages):
        for line in errors.splitlines():
            match = re.match(self.LINE_RE, line)

            lineNumber = int(match.group('line'))
            warning = match.group('warning')
            message = match.group('message')

            if warning:
                messages = warningMessages
                underlines = warningUnderlines
            else:
                messages = errorMessages
                underlines = errorUnderlines

            self.add_message(lineNumber, lines, message, messages)

    # Modified version of find_file from BaseLinter which supports directories
    # (in addtion to files) and returns a path vs the contents of the file.
    def find_file_or_dir(self, filename, view):
        '''Find a file or directory with the given name, starting in the view's
           directory, then ascending the file hierarchy up to root.'''
        path = view.file_name()

        # quit if the view is temporary
        if not path:
            return None

        dirname = os.path.dirname(path)

        while True:
            path = os.path.join(dirname, filename)

            if os.path.exists(path):
                return path

            # if we hit root, quit
            parent = os.path.dirname(dirname)

            if parent == dirname:
                return None
            else:
                dirname = parent
