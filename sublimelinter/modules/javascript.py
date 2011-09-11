# -*- coding: utf-8 -*-
# javascript.py - sublimelint package for checking Javascript files

import os
import json
import subprocess
import sublime

from module_utils import get_startupinfo

__all__ = ['run', 'language']
language = 'JavaScript'
description =\
'''* view.run_command("lint", "JavaScript")
        Turns background linter off and runs the JSHint linter
        (jshint, assumed to be on $PATH) on current view.
'''

jsc_path = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Resources/jsc'


def jshint_path():
    return os.path.join(os.path.dirname(__file__), 'libs', 'jshint')


def is_enabled():
    if os.path.exists(jsc_path):
        return (True, 'using JavaScriptCore')
    try:
        subprocess.call(['node', '-v'], startupinfo=get_startupinfo())
        return (True, 'using node.js')
    except OSError:
        return (False, 'JavaScriptCore or node.js is required')
    except Exception as ex:
        return (False, unicode(ex))


def check(codeString, filename, jshint_config):
    path = jshint_path()

    if os.path.exists(jsc_path):
        process = subprocess.Popen((jsc_path, os.path.join(path, 'jshint_jsc.js'), '--', str(codeString.count('\n')), jshint_config, path + os.path.sep),
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    startupinfo=get_startupinfo())
    else:
        process = subprocess.Popen(('node', os.path.join(path, 'jshint_node.js'), jshint_config),
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    startupinfo=get_startupinfo())

    result = process.communicate(codeString)

    if result:
        if process.returncode == 0:
            if result[0].startswith('jshint: '):
                print '{0}: {1}'.format(language, result[0][len('jshint: '):])
            else:
                return json.loads(result[0].strip() or '[]')
        else:
            print '{0}: {1}'.format(language, result[0])
    else:
        print '{0}: no result returned from jshint'

    return []


def run(code, view, filename='untitled'):

    jshint_config = json.dumps(view.settings().get("jshint_config") or {})

    try:
        errors = check(code, filename, jshint_config)
    except OSError as (errno, message):
        print 'SublimeLinter: error executing linter: {0}'.format(message)
        errors = []

    lines = set()
    underlines = []
    errorMessages = {}

    def addMessage(lineno, message):
        if lineno in errorMessages:
            errorMessages[lineno].append(message)
        else:
            errorMessages[lineno] = [message]

    def underlineRange(lineno, position, length=1):
        line = view.full_line(view.text_point(lineno, 0))
        position += line.begin()

        for i in xrange(length):
            underlines.append(sublime.Region(position + i))

    for error in errors:
        lineno = error['line'] - 1  # jshint uses one-based line numbers
        lines.add(lineno)

        # Remove trailing period from error message
        reason = error['reason']

        if reason[-1] == '.':
            reason = reason[:-1]

        addMessage(lineno, reason)
        underlineRange(lineno, error['character'] - 1)

    return lines, underlines, [], [], errorMessages, {}, {}
