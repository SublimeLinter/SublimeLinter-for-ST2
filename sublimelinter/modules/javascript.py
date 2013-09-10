import json
import re
import subprocess

from .base_linter import BaseLinter, INPUT_METHOD_TEMP_FILE, INPUT_METHOD_STDIN

CONFIG = {
    'language': 'JavaScript'
}


class Linter(BaseLinter):
    GJSLINT_RE = re.compile(r'Line (?P<line>\d+),\s*E:(?P<errnum>\d+):\s*(?P<message>.+)')

    def __init__(self, config):
        super(Linter, self).__init__(config)
        self.linter = None

    def get_executable(self, view, linterName=''):

        if (linterName == ''):
            self.linter = view.settings().get('javascript_linter', 'jshint')
            self.linter = self.linter.split(',')[0]
        else:
            self.linter = linterName

        self.linter = self.linter.strip()

        if (self.linter in ('jshint', 'jslint')):
            self.input_method = INPUT_METHOD_STDIN
            return self.get_javascript_engine(view)
        elif (self.linter == 'gjslint'):
            try:
                path = self.get_mapped_executable(view, 'gjslint')
                subprocess.call([path, '--help'], startupinfo=self.get_startupinfo())
                self.input_method = INPUT_METHOD_TEMP_FILE
                return (True, path, 'using gjslint')
            except OSError:
                return (False, '', 'gjslint cannot be found')
        else:
            return (False, '', '"{0}" is not a valid javascript linter'.format(self.linter))

    def get_lint_args(self, view, code, filename):
        if (self.linter == 'gjslint'):
            args = []
            gjslint_options = view.settings().get("gjslint_options", [])
            args.extend(gjslint_options)
            args.extend(['--nobeep', filename])
            return args
        elif (self.linter in ('jshint', 'jslint')):
            return self.get_javascript_args(view, self.linter, code)
        else:
            return []

    def get_javascript_options(self, view):
        if self.linter == 'jshint':
            rc_options = self.find_file('.jshintrc', view)

            if rc_options is not None:
                rc_options = self.strip_json_comments(rc_options)
                return json.dumps(json.loads(rc_options))

    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        if (self.linter == 'gjslint'):
            ignore = view.settings().get('gjslint_ignore', [])

            for line in errors.splitlines():
                match = self.GJSLINT_RE.match(line)

                if match:
                    line, errnum, message = match.group('line'), match.group('errnum'), match.group('message')

                    if (int(errnum) not in ignore):
                        self.add_message(int(line), lines, message, errorMessages)

        elif (self.linter in ('jshint', 'jslint')):
            try:
                errors = json.loads(errors.strip() or '[]')
            except ValueError:
                raise ValueError("Error from {0}: {1}".format(self.linter, errors))

            for error in errors:
                lineno = error['line']
                self.add_message(lineno, lines, error['reason'], errorMessages)
                self.underline_range(view, lineno, error['character'] - 1, errorUnderlines)

    def run(self, view, code, filename=None):
        self.filename = filename

        all_lines = set()
        all_errorUnderlines = []  # leave this here for compatibility with original plugin
        all_errorMessages = {}
        all_violationUnderlines = []
        all_violationMessages = {}
        all_warningUnderlines = []
        all_warningMessages = {}

        try:
            linters = view.settings().get('javascript_linter', 'jshint')
            linters = linters.split(',')

            for linter in linters:
                self.enabled, self.executable, message = self.get_executable(view, linter)

                if self.enabled:
                    if self.executable is None:
                        errors = self.built_in_check(view, code, filename)
                    else:
                        errors = self.executable_check(view, code, filename)

                    # Parse errors
                    lines = set()
                    errorUnderlines = []
                    errorMessages = {}
                    violationUnderlines = []
                    violationMessages = {}
                    warningUnderlines = []
                    warningMessages = {}
                    self.parse_errors(view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages)

                    #Merge errors
                    all_lines = all_lines.union(lines)
                    all_errorUnderlines += errorUnderlines
                    all_errorMessages.update(errorMessages)
                    all_violationUnderlines += violationUnderlines
                    all_violationMessages.update(violationMessages)
                    all_warningUnderlines += warningUnderlines
                    all_warningMessages.update(warningMessages)

        except Exception as ex:
            print('javascript.py run() Exception=' + str(ex, 'utf-8'))

        return all_lines, all_errorUnderlines, all_violationUnderlines, all_warningUnderlines, all_errorMessages, all_violationMessages, all_warningMessages
