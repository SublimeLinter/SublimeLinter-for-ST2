import re

from base_linter import BaseLinter, INPUT_METHOD_FILE

CONFIG = {
    'language': 'rubocop',
    'executable': 'rubocop',
    'lint_args': ['-f','s','{filename}'],
    'input_method': INPUT_METHOD_FILE
}


class Linter(BaseLinter):

    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        for line in errors.splitlines():
            match = re.match(r'^(?P<type>[WEC]):\s?\s?(?P<line>\d+): (?P<error>.*)', line)

            if match:
                error_type = match.group('type')
                error = match.group('error')
                line = int(match.group('line'))

                if error_type == 'W' or error_type == 'C':
                    messages = warningMessages
                else:
                    messages = errorMessages

                self.add_message(line, lines, error, messages)
