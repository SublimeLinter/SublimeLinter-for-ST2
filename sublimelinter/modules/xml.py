# -*- coding: utf-8 -*-
# html.py - sublimelint package for checking html files

from xmllint_linter import XmllintLinter

CONFIG = {
    'language': 'xml',
    'executable': 'xmllint',
    'lint_args': ['-noout', '-']
}


class Linter(XmllintLinter):
  pass
