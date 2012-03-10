# -*- coding: utf-8 -*-
# css.py - sublimelint package for checking CSS files

import os
import json
import subprocess

from base_linter import BaseLinter

CONFIG = {
    'language': 'CSS'
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
        path = self.csslint_path()
        csslint_options = json.dumps(view.settings().get("csslint_options") or {})

        # if self.use_jsc:
        #     args = (os.path.join(path, 'csslint_via_jsc.js'), '--', str(code.count('\n')), csslint_options, path + os.path.sep)
        # else:
        #     args = (os.path.join(path, 'csslint_via_node.js'), csslint_options)

        # I cannot test JSC so I am disabling it for the moment.
        args = (os.path.join(path, 'csslint_via_node.js'), csslint_options)

        return args

    def csslint_path(self):
        return os.path.join(os.path.dirname(__file__), 'libs', 'csslint')

    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        # print errors
        errors = json.loads(errors.strip() or '[]')

        for error in errors:
            lineno = error['line']
            self.add_message(lineno, lines, error['reason'], errorMessages)
            self.underline_range(view, lineno, error['character'] - 1, errorUnderlines)
