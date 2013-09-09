import re

from .base_linter import BaseLinter

CONFIG = {
    'language': 'ruby-tailor',
    'executable': 'tailor',
    'lint_args': '{filename}'
}


class Linter(BaseLinter):
    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        output = errors.splitlines()
        for index, line in enumerate(output):
            line_and_column_match = re.match(r'^.+position:  (?P<line>\d+):(?P<column>\d+)', line)
            if line_and_column_match:
                # get the message text that's 2 lines ahead
                message_match = re.match(r'^.+message:   (?P<error>.+)', output[index+2])
                line = int(line_and_column_match.group('line'))
                column = int(line_and_column_match.group('column'))
                error = message_match.group('error')

                if line == '<EOF>':
                    # Not sure what to do for EOF errors
                    line = '1'
                self.add_message(line, lines, error, errorMessages)
                self.underline_range(view, line, column, errorUnderlines)