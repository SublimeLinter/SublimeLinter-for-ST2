# -*- coding: utf-8 -*-

import re
from base_linter import BaseLinter, INPUT_METHOD_TEMP_FILE

CONFIG = {
  'language': 'Matlab',
  'executable': 'mlint',
  'lint_args': '{filename}',
  'input_method': INPUT_METHOD_TEMP_FILE
}


class Linter(BaseLinter):

  MATLAB_RE = re.compile(r'^L (?P<line>\d+) \(C (?P<cstart>\d+)(-(?P<cend>\d+))?\): (?P<error>.*)')

  def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
    for line in errors.splitlines():
      match = self.MATLAB_RE.match(line)
      if match:
        error, line, cstart, cend = match.group('error'), match.group('line'), match.group('cstart'), match.group('cend')
        # distinguishing between linter errors and warnings would require
        # running 'mlint' twice with different arguments, hence everything
        # is currently considered a warning
        self.add_message(int(line), lines, error, warningMessages)
        # underline
        ulength = int(cend)-int(cstart)+1 if cend else 1
        self.underline_range(view, int(line), int(cstart)-1, warningUnderlines, ulength)
