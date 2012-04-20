# -*- coding: utf-8 -*-
# perlcritic.py - sublimelint package for critiquing perl files

import re
import os
import subprocess

from base_linter import BaseLinter

CONFIG = {
    'language': 'perlcritic',
    'executable': 'perlcritic',
    'lint_args': ['--verbose', '8'],
}


class Linter(BaseLinter):

    def get_executable(self, view):
        """ check for perlcritic or perlcritic.bat (on windows machine) """
        exe = 'perlcritic'

        if os.name == 'nt':
            exe = 'perlcritic.bat'

        try:
            subprocess.call([exe, '--version'], startupinfo=self.get_startupinfo())
            return (True, exe, 'using ' + exe)
        except OSError:
            return (False, '', 'Perl::Critic is required')

    def executable_check(self, view, code, filename):
        # make sure get_executable() has run and everything is setup
        self.check_enabled(view)
        # return the normal executable_check()
        return super(Linter, self).executable_check(view, code, filename)

    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        for line in errors.splitlines():
            # I like to see these errors in the console
            print(line)
            match = re.match(r'\[(?P<pbp>.+)\] (?P<error>.+?) at line (?P<line>\d+), column (?P<column>\d+).+?', line)

            if match:
                error, line, column = match.group('error'), match.group('line'), match.group('column')
                lineno = int(line)
                column = int(column) - 1

                self.add_message(lineno, lines, error, errorMessages)
                self.underline_word(view, lineno, column, errorUnderlines)
