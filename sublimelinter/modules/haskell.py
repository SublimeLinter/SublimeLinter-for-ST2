# -*- coding: utf-8 -*-
# php.py - sublimelint package for checking php files

import re
import tempfile

from base_linter import BaseLinter, INPUT_METHOD_FILE, INPUT_METHOD_TEMP_FILE

CONFIG = {
    'language': 'haskell',
    'executable': 'hlint',
    'input_method': INPUT_METHOD_FILE
    #'lint_args': '{filename}'
}


class Linter(BaseLinter):
    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        i = 0
        errorLines = errors.splitlines()
        while i < len(errorLines):
            warning = re.match(r'^.+:(?P<line>\d+):(?P<col>\d+):.+:(?P<error>.+)', errorLines[i])

            if warning:
                errorFound = warning.group('error')
                errorLineNo = int(warning.group('line'))
                errorColNo = int(warning.group('col')) - 1
                errorLength = 0
                i += 2

                while errorLines[i] != "Why not:":
                    errorLength += len(errorLines[i].strip())
                    i += 1

                self.add_message(errorLineNo, lines, errorFound, errorMessages)

                j = 0
                while errorLength > 0:
                    lineText = view.substr(view.full_line(view.text_point(errorLineNo + j - 1, 0)))
                    startOffset = errorColNo if j == 0 else len(lineText) - len(lineText.lstrip())
                    underLineLength = len(lineText) - startOffset - 1
                    self.underline_range(view, errorLineNo + j, startOffset, warningUnderlines, underLineLength)
                    errorLength -= underLineLength
                    j += 1

                lines.add(errorLineNo)
            i += 1
