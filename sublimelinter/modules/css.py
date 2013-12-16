import json

from base_linter import BaseLinter

CONFIG = {
    'language': 'CSS'
}


class Linter(BaseLinter):
    def __init__(self, config):
        super(Linter, self).__init__(config)

    def get_executable(self, view):
        return self.get_javascript_engine(view)

    def get_lint_args(self, view, code, filename):
        return self.get_javascript_args(view, 'csslint', code)

    def get_javascript_options(self, view):
        rc_options = self.find_file('.csslintrc', view)

        if rc_options is not None:
            rc_options = self.strip_json_comments(rc_options)
            return json.dumps(json.loads(rc_options))

    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        try:
            errors = json.loads(errors.strip() or '[]')
        except ValueError:
            raise ValueError("Error from csslint: {0}".format(errors))

        for error in errors:
            lineno = error['line']

            if error['type'] == 'warning':
                messages = warningMessages
                underlines = warningUnderlines
            else:
                messages = errorMessages
                underlines = errorUnderlines

            self.add_message(lineno, lines, error['reason'], messages)
            self.underline_range(view, lineno, error['character'] - 1, underlines)
