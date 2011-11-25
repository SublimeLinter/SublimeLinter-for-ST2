# -*- coding: utf-8 -*-
# coffeescript.py - sublimelint package for checking coffee files

import re
import os

from base_linter import BaseLinter

CONFIG = {
    'language': 'coffeescript',
    'executable': 'coffee.cmd' if os.name == 'nt' else 'coffee',
    'lint_args': '-l'
}


class Linter(BaseLinter):
    def parse_errors(self, view, errors, lines, errorUnderlines,
                     violationUnderlines, warningUnderlines, errorMessages,
                     violationMessages, warningMessages):
        for line in errors.splitlines():
            match = re.match(r'.*?Error: In .+?, Parse error on line '
                             r'(?P<line>\d+): (?P<error>.+)', line)
            if not match:
                match = re.match(r'.*?Error: In .+?, (?P<error>.+) '
                                 r'on line (?P<line>\d+)', line)

            if match:
                line, error = match.group('line'), match.group('error')
                self.add_message(int(line), lines, error, errorMessages)
