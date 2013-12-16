import json

from base_linter import BaseLinter

CONFIG = {
    'language': 'reStructuredText',
    'executable': 'rst-lint',
    'lint_args': ['--format', 'json', '{filename}'],
}

class Linter(BaseLinter):
    def parse_errors(self, view, error_json, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        try:
            errors = json.loads(error_json)
        except ValueError as e:
            print('Could not parse rst.')
            print(error_json)
            raise e
        for error in errors:
            self.add_message(error['line'], lines, error['message'], errorMessages)
