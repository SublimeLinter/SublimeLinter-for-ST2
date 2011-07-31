''' sublime_pylint.py - sublimelint package for checking python files

pylint is not available as a checker that runs in the background
as it generally takes much too long.
'''

from StringIO import StringIO
import tempfile
try:
    from pylint import checkers
    from pylint import lint
    PYLINT_AVAILABLE = True
except ImportError:
    print "pylint is not available"
    PYLINT_AVAILABLE = False

language = 'pylint'
description =\
'''* view.run_command("lint", "pylint")
        Turns background linter off and runs pylint on current view.
'''


def run_pylint(code):
    '''runs pylint on the code using a temporary file for storage'''
    linter = lint.PyLinter()
    checkers.initialize(linter)
    # Disable some errors.
    linter.load_command_line_configuration([
        '--module-rgx=.*',  # don't check the module name
        '--reports=n',      # remove tables
        '--persistent=n',   # don't save the old score (no sense for temp)
    ])

    temp = tempfile.NamedTemporaryFile(suffix='.py')
    temp.write(code)
    temp.flush()

    output_buffer = StringIO()
    linter.reporter.set_output(output_buffer)
    linter.check(temp.name)
    _report = output_buffer.getvalue().replace(temp.name, 'line ')

    output_buffer.close()
    temp.close()

    return _report


def remove_unwanted(errors):
    '''remove unwanted warnings'''
    ## todo: investigate how this can be set by a user preference
    #  as it appears that the user pylint configuration file is ignored.
    lines = errors.split('\n')
    wanted = []
    unwanted = ["Found indentation with tabs instead of spaces",
                "************* Module"]
    for line in lines:
        for not_include in unwanted:
            if not_include in line:
                break
        else:
            wanted.append(line)
    return '\n'.join(wanted)


def run(code, *dummy):
    '''the common entry point to all linters'''
    if not PYLINT_AVAILABLE:
        return [], [], [], [], {}, {}, {}

    errors = run_pylint(code)
    errors = remove_unwanted(errors)

    lines = set()
    error_messages = {}
    for line in errors.splitlines():
        info = line.split(":")
        try:
            lineno = info[1]
        except IndexError:
            print info
        message = ":".join(info[2:])
        lineno = int(lineno) - 1
        lines.add(lineno)
        if lineno in error_messages:
            error_messages[lineno].append(message)
        else:
            error_messages[lineno] = [message]

    return lines, [], [], [], error_messages, {}, {}
