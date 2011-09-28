# -*- coding: utf-8 -*-
# go.py - sublimelint package for checking Go files

import os
import subprocess
import sublime

from module_utils import get_startupinfo

__all__ = ['run', 'language']
language = 'Go'
description =\
'''* view.run_command("lint", "Go")
        Turns background linter off and runs the Go linter
        (eg gomake, assumed to be on $PATH) on current view.
'''


def is_enabled():
    try:
        subprocess.call(['gomake', '-v'], startupinfo=get_startupinfo())
        return (True, 'using gomake')
    except OSError:
        return (False, 'gomake is required')
    except Exception as ex:
        return (False, unicode(ex))


def check(code, filename):
    path = os.path.dirname(filename)

    print path

    process = subprocess.Popen(['gomake', '-C', path],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                startupinfo=get_startupinfo())

    result = process.communicate()

    if result:
        if process.returncode == 0:
            return []
        else:
            errors = []

            for pos, line in enumerate(result[0].split('\n')):
                parts = line.split(':', 2)
                if len(parts) != 3:
                    continue

                file_name, line_no, message = parts
                errors.append((file_name, int(line_no), message[1:]))

            return errors
    else:
        print '{0}: no result returned from gomake'

    return []


_cache = {}
def run(code, view, filename='untitled'):
    if view.is_dirty():
        return _cache.get(view.buffer_id(), ([], [], [], [], [], {}, {}))

    try:
        errors = check(code, filename)
    except OSError as (errno, message):
        print 'SublimeLinter: error executing linter: {0}'.format(message)
        errors = []

    lines = set()
    messages = {}

    expected_file_name = os.path.basename(filename)

    for file_name, line_no, reason in errors:
        if file_name != expected_file_name:
            continue

        lines.add(line_no - 1)
        messages.setdefault(line_no - 1, []).append(reason)

    _cache[view.buffer_id()] = lines, [], [], [], messages, {}, {}
    return _cache[view.buffer_id()]
