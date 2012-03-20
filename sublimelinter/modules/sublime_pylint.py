''' sublime_pylint.py - sublimelint package for checking python files

pylint is not available as a checker that runs in the background
as it generally takes much too long.
'''

from StringIO import StringIO
import tempfile

try:
    from pylint import checkers
    from pylint import lint
    PYLINT_AVAILABLE = True
except ImportError:
    PYLINT_AVAILABLE = False

import base_linter
from base_linter import BaseLinter

CONFIG = {
    'language': 'pylint',
    'executable': 'pylint',
    'lint_args': ('--reports=n', '--persistent=n', '--include-ids=y', '{filename}'),
    'input_method': base_linter.INPUT_METHOD_FILE,
}

class Linter(BaseLinter):
    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):

        def underline_word(lineno, word, underlines):
            regex = r'((and|or|not|if|elif|while|in)\s+|[+\-*^%%<>=\(\{{])*\s*(?P<underline>[\w\.]*{0}[\w]*)'.format(re.escape(word))
            self.underline_regex(view, lineno, regex, lines, underlines, word)

        def underline_import(lineno, word, underlines):
            linematch = '(from\s+[\w_\.]+\s+)?import\s+(?P<match>[^#;]+)'
            regex = '(^|\s+|,\s*|as\s+)(?P<underline>[\w]*{0}[\w]*)'.format(re.escape(word))
            self.underline_regex(view, lineno, regex, lines, underlines, word, linematch)

        def underline_for_var(lineno, word, underlines):
            regex = 'for\s+(?P<underline>[\w]*{0}[\w*])'.format(re.escape(word))
            self.underline_regex(view, lineno, regex, lines, underlines, word)

        def underline_duplicate_argument(lineno, word, underlines):
            regex = 'def [\w_]+\(.*?(?P<underline>[\w]*{0}[\w]*)'.format(re.escape(word))
            self.underline_regex(view, lineno, regex, lines, underlines, word)

        error_objs = []
        for line in errors.splitlines():
            info = line.split(":")
            if len(info) < 3: continue

            lineno = int(info[1].strip().split(',')[0])
            col = int(info[1].strip().split(',')[1])
            name = info[0][1:]
            level = info[0][0]

            if level == 'E':
                messages = errorMessages
                underlines = errorUnderlines
            elif level == 'C': # convention = violation?
                messages = violationMessages
                underlines = violationUnderlines
            elif level == 'W':
                messages = warningMessages
                underlines = warningUnderlines

            self.underline_range(view, lineno, col, underlines)

            self.add_message(lineno, lines, '{0}{1}: {2}'.format(level, name, ':'.join(info[2:])), messages)
