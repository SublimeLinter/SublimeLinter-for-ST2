# haskell.py - sublimelint package for checking haskell files

import subprocess
import sublime
import tempfile

from module_utils import get_executable, get_startupinfo


# start sublimelint Haskell plugin
import re
__all__ = ['run', 'language']
language = 'Haskell'
linter_executable = 'hlint'
description =\
'''* view.run_command("lint", "Haskell")
        Turns background linter off and runs the default Haskell linter
        (hlint, assumed to be on $PATH) on current view.
'''


def is_enabled():
    global linter_executable
    linter_executable = get_executable('hlint', 'hlint')

    try:
        subprocess.Popen((linter_executable, '-v'), startupinfo=get_startupinfo(),
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
    except OSError:
        return (False, '"{0}" cannot be found'.format(linter_executable))

    return (True, 'using "{0}" for executable'.format(linter_executable))


def check(codeString, filename):
    global linter_executable

    #hlint cannot take input on stdin so we need to create a temporary file
    #for it to read from - hopefully this will be remedied in future
    with tempfile.NamedTemporaryFile(mode='r+', delete=False) as tmpfile:
        tmpfile.write(codeString)
        tmpfile.close()  # windows cannot reopen an open file

        process = subprocess.Popen((linter_executable, tmpfile.name),
                      stdin=subprocess.PIPE,
                      stdout=subprocess.PIPE,
                      stderr=subprocess.STDOUT,
                      startupinfo=get_startupinfo())
        result = process.communicate()[0]

    return result


def run(code, view, filename='untitled'):
    errors = check(code, filename)

    lines = set()
    underline = []  # leave this here for compatibility with original plugin

    errorMessages = {}

    def addMessage(lineno, message):
        message = str(message)
        if lineno in errorMessages:
            errorMessages[lineno].append(message)
        else:
            errorMessages[lineno] = [message]

    def underlineColumn(lineno, column, length):
        line = view.full_line(view.text_point(lineno, 0))
        if column > line.size():  # in this case hlint has joined the lines
            underline.append(sublime.Region(view.text_point(lineno, column - 1)))
            # so just put warning marker at the end
            return
        for i in xrange(length):
            point = view.text_point(lineno, column + i)
            underline.append(sublime.Region(point))

    def underlineRegion(lineno, regex):
        line = view.full_line(view.text_point(lineno, 0))
        lineText = view.substr(line)
        match = re.search(regex, lineText)
        if match:
            start, end = match.start('underline'), match.end('underline')
            underlineColumn(lineno, start, end - start) 

    errorlines = errors.splitlines()
    i = 0
    while (i < len(errorlines)):
        match = re.match(r'^.+:(?P<line>\d+):\d+:.+:(?P<error>.+)', errorlines[i])

        if match:
            error, line = match.group('error'), match.group('line')
            found = errorlines[i + 2].strip()

            lineno = int(line) - 1
            lines.add(lineno)
            addMessage(lineno, error)

            reg = '(?P<underline>{0})'.format(re.escape(found)).replace(r"\ ", r"\ ?")
            underlineRegion(lineno, reg)
            i += 3

        i += 1

    return lines, underline, [], [], errorMessages, {}, {}
