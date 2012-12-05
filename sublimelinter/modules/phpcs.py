# -*- coding: utf-8 -*-
# php.py - sublimelint package for checking php files

import re
import csv
import json
from base_linter import BaseLinter

CONFIG = {
    'language': 'phpcs',
    'executable': '/usr/local/opt/php54/bin/phpcs',
    'lint_args': ['--report=csv'],
    'ignore': []
}


class Linter(BaseLinter):
    def get_lint_args(self, view, code, filename):
        lint_args = CONFIG['lint_args']
        options = self.get_phpcs_options(view)

        if 'standards' in options:
            for standard in options['standards']:
                lint_args.append("--standard=%s" % standard)

        return lint_args

    def get_executable(self, view):
        executable = CONFIG['executable']
        options = self.get_phpcs_options(view)
        if 'executable' in options:
            executable = options['executable']
        return (True, executable, "Executable: %s" % executable)

    def get_phpcs_options(self, view):
        options = view.settings().get('phpcs_options', [])

        phpcsrc = self.find_file('.phpcsrc', view)
        if phpcsrc:
            phpcsrc = self.strip_json_comments(phpcsrc)
            options = dict(options.items() + json.loads(phpcsrc).items())
        return options

    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        options = self.get_phpcs_options(view)

        ignore = CONFIG['ignore']
        if 'ignore' in options:
            ignore = options['ignore']

        # parse the errors from the CSV
        for line in errors.splitlines():
            print line
            for row in csv.reader([line]):
                if len(row) >= 6:
                    # if the first part of the CSV entry is not a number, then it is likely
                    # a header and not an error
                    if not re.match(r"\d+", row[1]):
                        continue

                    # ignore items in the ignore options
                    if row[5] in ignore:
                        continue
                    self.add_message(int(row[1]), lines, "%s (%s)" % (row[4], row[5]), errorMessages)
                else:
                    print line
