# -*- coding: utf-8 -*-
# php.py - sublimelint package for checking php files

import os
import platform

from re import match
from commands import getstatusoutput
from base_linter import BaseLinter, INPUT_METHOD_FILE


CONFIG = {
    'language': 'haskell',
    'input_method': INPUT_METHOD_FILE
}


class Linter(BaseLinter):
    def get_executable(self, view):
        _, hlint = getstatusoutput('which hlint')
        if len(hlint) is 0:
            osType = platform.system()
            homeDir = os.environ['HOME']
            if osType.startswith('Darwin'):  # OSX
                if os.path.exists(homeDir + '/Library/Haskell/bin/hlint'):  # Haskell platform
                    hlint = homeDir + '/Library/Haskell/bin/hlint'
            # TODO: Should do for other variations on OSX and other OS.

        if len(hlint) > 0:
            return (True, hlint, 'hLint loaded')
        else:  # Unknown system/install
            return (False, False, 'hLint not found. (Only finds on system path, and on OSX w/Haskell Platform, please add to source)')

    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        i = 0
        errorLines = errors.splitlines()
        while i < len(errorLines):
            warning = match(r'^.+:(?P<line>\d+):(?P<col>\d+):.+:(?P<error>.+)', errorLines[i])

            if warning:
                errorFound = warning.group('error')
                errorLineNo = int(warning.group('line'))
                errorColNo = int(warning.group('col')) - 1
                errorLength = 0
                i += 2

                while errorLines[i] != "Why not:":  # Zoidberg?
                    errorLength += len(errorLines[i].strip())
                    i += 1

                self.add_message(errorLineNo, lines, errorFound, errorMessages)
                lines.add(errorLineNo)

                j = 0
                while errorLength > 0:
                    lineText = view.substr(view.full_line(view.text_point(errorLineNo + j - 1, 0)))
                    startOffset = errorColNo if j == 0 else len(lineText) - len(lineText.lstrip())
                    underLineLength = len(lineText) - startOffset - 1
                    self.underline_range(view, errorLineNo + j, startOffset, warningUnderlines, underLineLength)
                    errorLength -= underLineLength
                    j += 1
            i += 1
