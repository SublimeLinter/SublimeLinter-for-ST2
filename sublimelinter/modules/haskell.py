# -*- coding: utf-8 -*-
# php.py - sublimelint package for checking php files

import re
import tempfile

from base_linter import BaseLinter, INPUT_METHOD_FILE, INPUT_METHOD_TEMP_FILE

CONFIG = {
    'language': 'haskell',
    'executable': 'hlint',
    'input_method': INPUT_METHOD_FILE,
    'lint_args': '{filename}'
}


class Linter(BaseLinter):
    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        i = 0
        errorLines = errors.splitlines()
        print len(errorLines)
        while i < len(errorLines):
            #print errorLines[i] + " "
            match = re.match(r'^.+:(?P<line>\d+):\d+:.+:(?P<error>.+)', errorLines[i])

            if match:
                error, line = match.group('error'), match.group('line')
                print "error" + error + " " + line + "\n"
                found = errorLines[i + 2].strip()
                #print found

                lineno = int(line)
                lines.add(lineno)
                self.add_message(lineno, lines, error, errorMessages)

                #reg = '(?P<underline>{0})'.format(re.escape(found)).replace(r"\ ", r"\ ?")
                #self.underlineRegion(lineno, reg)
                i += 3

            i += 1
