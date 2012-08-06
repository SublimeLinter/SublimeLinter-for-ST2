# -*- coding: utf-8 -*-
# html.py - sublimelint package for checking html files

from xmllint_linter import XmllintLinter

CONFIG = {
    'language': 'html',
    'executable': 'xmllint',
    'lint_args': ['-html', '-noout', '-']
}


class Linter(XmllintLinter):
  pass
