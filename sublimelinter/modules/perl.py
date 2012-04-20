# -*- coding: utf-8 -*-
# perl.py - sublimelint package for checking perl files

import re
import os
import subprocess

from base_linter import BaseLinter

CONFIG = {
    'language': 'perl',
    'perl_args': '-c',
    'perlcritic_args': ['--verbose', '8']
}


class Linter(BaseLinter):

    def __init__(self, config):
        super(Linter, self).__init__(config)
        self.use_perlcritic = False
        self.config = config

    def get_executable(self, view):
        """ Test for perlcritic (or perlcritic.bat on NT), else test for Perl, else nothing """
        perlcritic = 'perlcritic'

        if os.name == 'nt':
            perlcritic = 'perlcritic.bat'

        try:
            subprocess.call([perlcritic, '--version'], startupinfo=self.get_startupinfo())
            self.use_perlcritic = True
            return (True, perlcritic, 'using Perl::Critic -- {0}'.format(perlcritic))
        except OSError:
            try:
                subprocess.call(['perl', '-v'], startupinfo=self.get_startupinfo())
                return (True, 'perl', 'using Perl executable')
            except OSError:
                return (False, '', 'Perl or Perl::Critic is required')

    def get_lint_args(self, view, code, filename):
        if self.use_perlcritic:
            return self.config.get('perlcritic_args')
        else:
            return self.config.get('perl_args')

    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        """ redirect to parse_perlcritic_errors or parse_perl_errors """
        if self.use_perlcritic:
            self.parse_perlcritic_errors(view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages)
        else:
            self.parse_perl_errors(view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages)

    def parse_perlcritic_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        """ deal with messages from perlcritic """
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

    def parse_perl_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        """ deal with messages from perl """
        for line in errors.splitlines():
            match = re.match(r'(?P<error>.+?) at .+? line (?P<line>\d+)(, near "(?P<near>.+?)")?', line)

            if match:
                error, line = match.group('error'), match.group('line')
                lineno = int(line)
                near = match.group('near')

                if near:
                    error = '{0}, near "{1}"'.format(error, near)
                    self.underline_regex(view, lineno, '(?P<underline>{0})'.format(re.escape(near)), lines, errorUnderlines)

                self.add_message(lineno, lines, error, errorMessages)
