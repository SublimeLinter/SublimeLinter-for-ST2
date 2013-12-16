import pyflakes.checker as pyflakes
import _ast


class PythonLintError(pyflakes.messages.Message):

    def __init__(self, filename, loc, level, message, message_args, offset=None, text=None):
        super(PythonLintError, self).__init__(filename, loc)
        self.level = level
        self.message = message
        self.message_args = message_args
        if offset is not None:
            self.offset = offset
        if text is not None:
            self.text = text


class Pep8Error(PythonLintError):

    def __init__(self, filename, loc, offset, code, text):
        # PEP 8 Errors are downgraded to "warnings"
        super(Pep8Error, self).__init__(filename, loc, 'W', '[W] PEP 8 (%s): %s', (code, text),
                                        offset=offset, text=text)


class Pep8Warning(PythonLintError):

    def __init__(self, filename, loc, offset, code, text):
        # PEP 8 Warnings are downgraded to "violations"
        super(Pep8Warning, self).__init__(filename, loc, 'V', '[V] PEP 8 (%s): %s', (code, text),
                                          offset=offset, text=text)


class OffsetError(PythonLintError):

    def __init__(self, filename, loc, text, offset):
        super(OffsetError, self).__init__(filename, loc, 'E', '[E] %r', (text,), offset=offset + 1, text=text)


class PythonError(PythonLintError):
    def __init__(self, filename, loc, text):
        super(PythonError, self).__init__(filename, loc, 'E', '[E] %r', (text,), text=text)


def pyflakes_check(code, filename, ignore=None):
    try:
        tree = compile(code, filename, "exec", _ast.PyCF_ONLY_AST)
        w = pyflakes.Checker(tree, filename)

    except (SyntaxError, IndentationError), value:
        msg = value.args[0]

        (lineno, offset, text) = value.lineno, value.offset, value.text

        # If there's an encoding problem with the file, the text is None.
        if text is None:
            # Avoid using msg, since for the only known case, it contains a
            # bogus message that claims the encoding the file declared was
            # unknown.
            if msg.startswith('duplicate argument'):
                arg = msg.split('duplicate argument ', 1)[1].split(' ', 1)[0].strip('\'"')
                error = pyflakes.messages.DuplicateArgument(filename, value, arg)
            else:
                error = PythonError(filename, value, msg)
        else:
            line = text.splitlines()[-1]

            if offset is not None:
                offset = offset - (len(text) - len(line))

            if offset is not None:
                error = OffsetError(filename, value, msg, offset)
            else:
                error = PythonError(filename, value, msg)
        return [error]
    except ValueError, e:
        return [PythonError(filename, 0, e.args[0])]
    else:
        # Okay, it's syntactically valid.  Now check it.
        if ignore is not None:
            old_magic_globals = pyflakes._MAGIC_GLOBALS
            pyflakes._MAGIC_GLOBALS += ignore

        w = pyflakes.Checker(tree, filename)

        if ignore is not None:
            pyflakes._MAGIC_GLOBALS = old_magic_globals

        return w.messages
