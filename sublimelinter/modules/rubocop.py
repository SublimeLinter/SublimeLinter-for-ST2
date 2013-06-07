import re

from base_linter import BaseLinter, INPUT_METHOD_TEMP_FILE

CONFIG = {
    'language': 'rubocop',
    'executable': 'rubocop',
    'lint_args': "{filename}",
    'input_method': INPUT_METHOD_TEMP_FILE
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
                    underlines = warningUnderlines
                else:
                    messages = errorMessages
                    underlines = errorUnderlines

                self.add_message(line, lines, error, messages)

                # Rubocop does not return the column so I could remove this line
                # I decided to put an underscore at column 0 because sometimes
                # the gutter can colide with other plugins.
                self.underline_range(view, line, 0, underlines)
