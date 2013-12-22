import re

from base_linter import BaseLinter

CONFIG = {
    'language': 'Ruby',
    'executable': 'ruby',
    'lint_args': '-wc'
}


class Linter(BaseLinter):
    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        for line in errors.splitlines():
            match = re.match(r'^.+:(?P<line>\d+):\s+(?P<error>.+)', line)

            if match:
                message, line = match.group('error'), match.group('line')

                if re.match(r'\Awarning:', message):
                    messages = warningMessages
                else:
                    messages = errorMessages

                self.add_message(int(line), lines, message, messages)
