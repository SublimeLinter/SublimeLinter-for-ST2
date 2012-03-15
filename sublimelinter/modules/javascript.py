# -*- coding: utf-8 -*-
# javascript.py - sublimelint package for checking Javascript files

import os
import json
import subprocess

from base_linter import BaseLinter

CONFIG = {
    'language': 'JavaScript'
}


class Linter(BaseLinter):
    JSC_PATH = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Resources/jsc'

    def __init__(self, config):
        super(Linter, self).__init__(config)
        self.use_jsc = False

    def get_executable(self, view):
        if os.path.exists(self.JSC_PATH):
            self.use_jsc = True
            return (True, self.JSC_PATH, 'using JavaScriptCore')
        try:
            path = self.get_mapped_executable(view, 'node')
            subprocess.call([path, '-v'], startupinfo=self.get_startupinfo())
            return (True, path, '')
        except OSError:
            return (False, '', 'JavaScriptCore or node.js is required')

    def get_lint_args(self, view, code, filename):
        options = view.settings()
        linter = options.get('sublimelinter_javascript_linter') or 'jshint'
        path = os.path.join(os.path.dirname(__file__), 'libs', linter)
        linter_options = json.dumps(options.get('%s_options' % linter) or {})

        if self.use_jsc:
            args = (os.path.join(path, '%s_jsc.js' % linter), '--', str(code.count('\n')), linter_options, path + os.path.sep)
        else:
            args = (os.path.join(path, '%s_node.js' % linter), linter_options)

        return args

    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        errors = json.loads(errors.strip() or '[]')

        for error in errors:
            lineno = error['line']
            self.add_message(lineno, lines, error['reason'], errorMessages)
            self.underline_range(view, lineno, error['character'] - 1, errorUnderlines)
