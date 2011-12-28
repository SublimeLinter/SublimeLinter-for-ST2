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
        self.jshint_options = None

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
        path = self.jshint_path()

        if self.jshint_options is None:
            self.jshint_options = json.dumps(view.settings().get("jshint_options") or {})

        if self.use_jsc:
            args = (os.path.join(path, 'jshint_jsc.js'), '--', str(code.count('\n')), self.jshint_options, path + os.path.sep)
        else:
            args = (os.path.join(path, 'jshint_node.js'), self.jshint_options)

        return args

    def jshint_path(self):
        return os.path.join(os.path.dirname(__file__), 'libs', 'jshint')

    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        errors = json.loads(errors.strip() or '[]')

        for error in errors:
            lineno = error['line']
            self.add_message(lineno, lines, error['reason'], errorMessages)
            self.underline_range(view, lineno, error['character'] - 1, errorUnderlines)
