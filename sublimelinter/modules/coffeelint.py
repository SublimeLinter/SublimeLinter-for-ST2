# -*- coding: utf-8 -*-
# coffeelint.py - sublimelint package for checking coffee files
# based on coffeescript.py, inspired by https://github.com/clutchski/coffeelint

import re
import os

from base_linter import BaseLinter

CONFIG = {
    'language': 'coffeescript',
    'executable': 'coffeelint.cmd' if os.name == 'nt' else 'coffeelint',
    'lint_args': '--stdin'
}


class Linter(BaseLinter):
    def parse_errors(self, view, errors, lines, errorUnderlines,
                     violationUnderlines, warningUnderlines, errorMessages,
                     violationMessages, warningMessages):

        for line in errors.splitlines():
            match = re.match(r'#(?P<line>\d+) : (?P<type>[a-z]+) : (?P<err>.+)',
                            line)
            if match:
                line, err_text = int(match.group('line')), match.group('err')
                err_type = match.group('type')

                grp = errorMessages if err_type == 'error' else warningMessages

                self.add_message(line, lines, err_text, grp)
