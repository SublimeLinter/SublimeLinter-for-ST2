# -*- coding: utf-8 -*-
# python.py - sublimelint package for checking python files with flake8

import re

from .base_linter import BaseLinter

CONFIG = {
    'language': 'Python',
    'executable': 'flake8',
    'lint_args': '{filename}',
    'input_method': 3,
}


class Linter(BaseLinter):
    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        for line in errors.splitlines():
            match = re.match(r'^.+:(?P<line>\d+):(?P<offset>\d+):?\s+(?P<error>.+)', line)

            if match:
                error, line, offset = match.group('error'), match.group('line'), match.group('offset')
                self.add_message(int(line), lines, error, errorMessages)
                if offset:
                    self.underline_range(view, int(line), int(offset), errorUnderlines)
