# -*- coding: utf-8 -*-
# cpp.py - sublimelint package for checking C files

import cpp

CONFIG = {
    'language': 'C',
}

# Load configuration from C++
for prop in ['executable', 'lint_args', 'input_method']:
    CONFIG[prop] = cpp.CONFIG[prop]

class Linter(cpp.Linter):
    def __init__(self, config):
        super(Linter, self).__init__(config)
