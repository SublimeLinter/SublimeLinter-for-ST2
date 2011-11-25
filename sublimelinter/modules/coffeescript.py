# -*- coding: utf-8 -*-
# coffeescript.py - sublimelint package for checking coffee files

import re
import subprocess
import itertools

from base_linter import BaseLinter

CONFIG = {
    'language': 'coffeescript',
    'lint_args': '-l'
}


class Linter(BaseLinter):

    def get_executable(self, view):
        candidates = ["coffee", "coffee.cmd"]
        for try_executable_result in itertools.imap(self.try_executable, candidates):
            if try_executable_result[0]:
                return try_executable_result
        return (False, '', "coffee or coffee.cmd (windows) is required ")

    def try_executable(self, executable):
        try:
            subprocess.call([executable, '-v'], startupinfo=self.get_startupinfo())
            return (True, executable, '')
        except OSError:
            return (False, '', executable + ' is not present')

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
