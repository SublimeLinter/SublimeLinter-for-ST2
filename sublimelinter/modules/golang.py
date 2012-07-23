# -*- coding: utf-8 -*-
# golang.py - sublimelint package for checking golang files

import re

from base_linter import BaseLinter, INPUT_METHOD_FILE

CONFIG = {
    'language': 'go',
    'executable': '6g', # hard to autodetect; should be an option TODO
    'lint_args': ['-o', '/dev/null', '{filename}'],
    'input_method': INPUT_METHOD_FILE
}

class Linter(BaseLinter):
    def parse_errors(self, view, errors, lines, errorUnderlines,
                     violationUnderlines, warningUnderlines, errorMessages,
                     violationMessages, warningMessages):

        print errors
        for line in errors.splitlines():
            #match = re.match(r'.*?Error: In .+?, Parse error on line '
            #                 r'(?P<line>\d+): (?P<error>.+)', line)
            #if not match:
            #    match = re.match(r'.*?Error: In .+?, (?P<error>.+) '
            #                     r'on line (?P<line>\d+)', line)

            match = re.match(r'(.*?):(.*?):(.*)', line)
            if match:
                line, error = match.group(2), match.group(3)
                self.add_message(int(line), lines, error, errorMessages)
