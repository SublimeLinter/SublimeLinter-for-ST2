import re

from base_linter import BaseLinter, INPUT_METHOD_TEMP_FILE

CONFIG = {
    'language': 'ruby-lint',
    'executable': 'ruby-lint',
    'lint_args': '{filename}',
    'input_method': INPUT_METHOD_TEMP_FILE
}


class Linter(BaseLinter):

    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        for line in errors.splitlines():
            match = re.match(r'^.+: (?P<type>.+): line (?P<line>\d+), column (?P<column>\d+):\s+(?P<error>.+)', line)

            if match:
                error_type, error, line, column = match.group('type'), match.group('error'), match.group('line'), match.group('column')
                line = int(line)
                column = int(column)
                error = '[{0}] {1}'.format(error_type[0].upper(), error)

                if error_type == 'warning':
                    messages = warningMessages
                    underlines = warningUnderlines
                else:
                    messages = errorMessages
                    underlines = errorUnderlines

                self.add_message(line, lines, error, messages)
                self.underline_range(view, line, column, underlines)
