# -*- coding: utf-8 -*-
# latex.py - sublimelint package for checking latex files

import re

from base_linter import BaseLinter

CONFIG = {
    'language': 'LaTeX',
    'executable': 'chktex',
    'lint_args': ['-n1', '-n2', '-n3', "-f%l:%c %k %m\n"]
}


class Linter(BaseLinter):
    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        for line in errors.splitlines():
            match = re.match(r'^(?P<line>\d+):(?P<column>\d+) (?P<type>[^\s]+) (?P<error>.+)', line)
            if match:
                error, line, column, error_type = match.group('error'), match.group('line'), match.group('column'), match.group('type')
                messages = {
                    'Warning': warningMessages,
                    'Message': warningMessages,
                    'Error': errorMessages
                }[error_type]
                underlines = {
                    'Warning': warningUnderlines,
                    'Message': warningUnderlines,
                    'Error': errorUnderlines
                }[error_type]
                self.add_message(int(line), lines, error, messages)
                self.underline_range(view, int(line), int(column), underlines, length=1)
