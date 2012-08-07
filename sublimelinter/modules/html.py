# -*- coding: utf-8 -*-
# html.py - sublimelint package for checking html files

# Example error messages
#
# line 1 column 1 - Warning: missing <!DOCTYPE> declaration
# line 200 column 1 - Warning: discarding unexpected </div>
# line 1 column 1 - Warning: inserting missing 'title' element

import re

from base_linter import BaseLinter

CONFIG = {
    'language': 'html',
    'executable': 'tidy',
    'lint_args': '-eq'
}


class Linter(BaseLinter):
    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        for line in errors.splitlines():
            match = re.match(r'^line\s(?P<line>\d+)\scolumn\s\d+\s-\s(?P<error>.+)', line)

            if match:
                error, line = match.group('error'), match.group('line')
                self.add_message(int(line), lines, error, errorMessages)

