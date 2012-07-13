# -*- coding: utf-8 -*-
# haml.py - sublimelint package for checking haml files
# Save in your sublimelint folder, for example Mac OSX: ~/Library/Application Support/Sublime Text 2/Packages/SublimeLinter/sublimelinter/modules

import re

from base_linter import BaseLinter

CONFIG = {
    'language': 'ruby haml',
    'executable': 'haml',
    'lint_args': '-c'
}


class Linter(BaseLinter):
    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        for line in errors.splitlines():
            match = re.match(r'^.+(?P<line>\d+):\s+(?P<error>.+)', line)

            if match:
                error, line = match.group('error'), match.group('line')
                self.add_message(int(line), lines, error, errorMessages)
