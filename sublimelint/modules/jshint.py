# jshint.py - sublimelint package for checking Javascript files

import subprocess
import os
import sublime


def check(codeString, filename):
    info = None
    if os.name == 'nt':
        info = subprocess.STARTUPINFO()
        info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = subprocess.SW_HIDE

    process = subprocess.Popen(('jshint', filename),
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                startupinfo=info)

    lines = process.stdout.readlines()
    return lines


# start sublimelint jshint plugin
import re
__all__ = ['run', 'language']
language = 'JavaScript'
description =\
'''* view.run_command("lint", "JavaScript")
        Turns background linter off and runs the JSHint linter
        (jshint, assumed to be on $PATH) on current view.
'''


def run(code, view, filename='untitled'):
    try:
        errors = check(code, filename)
    except OSError:
        print 'jshint is not available'
        errors = []

    lines = set()
    underline = []  # leave this here for compatibility with original plugin

    errorMessages = {}

    def addMessage(lineno, message):
        message = str(message)
        if lineno in errorMessages:
            errorMessages[lineno].append(message)
        else:
            errorMessages[lineno] = [message]

    def underlineRange(lineno, position, length=1):
        line = view.full_line(view.text_point(lineno, 0))
        position += line.begin()

        for i in xrange(length):
            underline.append(sublime.Region(position + i))

    def underlineRegex(lineno, regex, wordmatch=None, linematch=None):
        lines.add(lineno)
        offset = 0

        line = view.full_line(view.text_point(lineno, 0))
        lineText = view.substr(line)
        if linematch:
            match = re.match(linematch, lineText)
            if match:
                lineText = match.group('match')
                offset = match.start('match')
            else:
                return

        iters = re.finditer(regex, lineText)
        results = [(result.start('underline'),
                    result.end('underline')) for result in iters if
                    not wordmatch or result.group('underline') == wordmatch]

        for start, end in results:
            underlineRange(lineno, start + offset, end - start)

    for line in errors:
        match = re.match(r'.* line (?P<line>\d+), col (?P<near>.+?)?, (?P<error>.+?)\.', line)

        if match:
            error, line = match.group('error'), match.group('line')
            lineno = int(line) - 1

            near = match.group('near')
            if near:
                error = '%s, near "%s"' % (error, near)
                underlineRegex(lineno, '(?P<underline>%s)' % near)

            lines.add(lineno)
            addMessage(lineno, error)

    return lines, underline, [], [], errorMessages, {}, {}
