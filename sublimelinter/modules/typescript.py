# -*- coding: utf-8 -*-
# typescript.py - sublimelint package for checking TypeScript files

import json

from base_linter import BaseLinter

CONFIG = {
    'language': 'TypeScript'
}


class Linter(BaseLinter):
    def __init__(self, config):
        super(Linter, self).__init__(config)

    def get_executable(self, view):
        return self.get_javascript_engine(view)

    def get_lint_args(self, view, code, filename):
        self.filename = filename
        return self.get_javascript_args(view, 'typescript', code)

    def get_javascript_options(self, view):
        return json.dumps({"filename": self.filename})

    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        try:
            errors = json.loads(errors.strip() or '[]')
        except ValueError:
            raise ValueError("Error from TypeScript: {0}".format(errors))

        for error in errors:
            lineno = error['line']

            self.add_message(lineno, lines, error['reason'], errorMessages)
            self.underline_range(view, lineno, error['character'] - 1, errorUnderlines)
