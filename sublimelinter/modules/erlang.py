# -*- coding: utf-8 -*-
# erlang.py - sublimelint package for checking erlang files
# Note: Use project file to add any additional paths you want
#       to add to the compiler.
#       ie.
#       "settings":
#       {
#               "SublimeLinter":
#               {
#                   "linter_args":
#                   {
#                       "erlang":
#                       [
#                           "/Users/joe/projects/myproj/libs/libA/ebin",
#                           "/Users/joe/projects/myproj/libs/libB/ebin",
#                           "/Users/joe/projects/myproj/deps/depA/ebin"
#                       ]
#                   }
#               }
#       }

import os
import re

from base_linter import BaseLinter, INPUT_METHOD_TEMP_FILE

eflymake = os.path.abspath(os.path.join(os.path.dirname(__file__), "libs/eflymake"))

CONFIG = {
    'language': 'erlang',
    'executable': 'escript',
    'lint_args': [eflymake, "{filename}"],
    'input_method': INPUT_METHOD_TEMP_FILE,
  #  'tempfile_suffix': ".erl",
    'test_existence_args': ' ',
}


class Linter(BaseLinter):
    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        for line in errors.splitlines():
            match = re.match(r'.+:(?P<line>\d+):\s*(?P<error>.+)', line)

            if match:
                error, line = match.group('error'), match.group('line')
                self.add_message(int(line), lines, error, errorMessages)
