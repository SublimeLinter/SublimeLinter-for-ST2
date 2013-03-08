# -*- coding: utf-8 -*-
# ruby.py - sublimelint package for checking ruby files

import re

from base_linter import BaseLinter, INPUT_METHOD_TEMP_FILE

CONFIG = {
    'language': 'ruby-lint',
    'executable': 'ruby-lint',
    'lint_args': '{filename}',
    'input_method': INPUT_METHOD_TEMP_FILE
}


class Linter(BaseLinter):

    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        for line in errors.splitlines():
            match = re.match(r'^.+: (?P<type>.+): line (?P<line>\d+), column \d+:\s+(?P<error>.+)', line)

            if match:
                error_type, error, line = match.group('type'), match.group('error'), match.group('line')
                error = '[{0}] {1}'.format(error_type[0].upper(), error)
                self.add_message(int(line), lines, error, errorMessages)
