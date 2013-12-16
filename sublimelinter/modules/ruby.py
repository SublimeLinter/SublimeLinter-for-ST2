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
            match = re.match(r'^.+:(?P<line>\d+):\s+(?P<type>warning: )?(?P<error>.+)', line)

            if match:
                error, warn, line = match.group('error'), match.group('type'), match.group('line')
                if warn:
                    self.add_message(int(line), lines, error, warningMessages)
                else:
                    self.add_message(int(line), lines, error, errorMessages)
