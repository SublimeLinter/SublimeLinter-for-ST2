import re
from base_linter import BaseLinter, INPUT_METHOD_FILE


CONFIG = {
    'language': 'haskell',
    'executable': 'hlint',
    'input_method': INPUT_METHOD_FILE,
    'lint_args': '{filename}'
}


class Linter(BaseLinter):
    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        i = 0
        error_lines = errors.splitlines()
        while i < len(error_lines):
            error = re.match(r'^.+:(?P<line>\d+):(?P<col>\d+): (?P<error>.+)', error_lines[i])

            if error:
                message, lineno, col = error.group('error'), int(error.group('line')), int(error.group('col'))

                if error_lines[i + 1] == "Error message:":
                    message = error_lines[i + 2]
                    i += 2

                lint_error = re.match(r'^(?P<type>Error|Warning): (?P<error>.+)', message)

                if lint_error:
                    error_type, message = lint_error.group('type'), lint_error.group('error')

                    if error_type == 'Warning':
                        messages = warningMessages
                        underlines = warningUnderlines
                    else:
                        messages = errorMessages
                        underlines = errorUnderlines

                self.add_message(lineno, lines, message, messages)
                self.underline_range(view, lineno, col - 1, underlines)

            i += 1
