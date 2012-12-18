import re
import os
import subprocess

try:
    import simplejson
except ImportError:
    import json as simplejson

from base_linter import BaseLinter, TEMPFILES_DIR

CONFIG = {'language': 'CoffeeScript'}


class Linter(BaseLinter):
    coffeelint_config = {}

    def _test_executable(self, executable):
        try:
            args = [executable]
            args.extend(self.test_existence_args)
            subprocess.Popen(
                args,
                startupinfo=self.get_startupinfo(),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            ).communicate()
            return True
        except OSError:
            return False

    def get_executable(self, view):
        if os.name == 'nt':
            lint_command, coffee_command = (
                'coffeelint.cmd',
                'coffee.cmd',
            )
        else:
            lint_command, coffee_command = (
                'coffeelint',
                'coffee',
            )

        executable = None

        if self._test_executable(lint_command):
            executable = lint_command
            self.mode = 'coffeelint'
        elif self._test_executable(coffee_command):
            self.mode = 'coffee'
            executable = coffee_command

        enabled = executable != None

        return (
            enabled,
            executable,
            'using "%s" for executable' % executable if enabled else 'neither coffeelint nor coffee are avaliable'
        )

    def get_lint_args(self, view, code, filename):
        print "GETTING THE ARGS FOR CoffeeScript"
        print "bt-dubs, the tab size is:" + str(view.settings().get('tab_size', 8))
        if self.mode == 'coffeelint':
            args = [
                '--stdin',
                '--nocolor',
                '--csv',
            ]

            new_config = view.settings().get('coffeelint_options', {})

            if new_config != {}:
                # smart config setup here

                if new_config != self.coffeelint_config:
                    self.coffeelint_config = new_config
                    self.write_config_file()

                args += ['--file', self.coffeelint_config_file]

            return args
        else:
            return ('-s', '-l')

    def parse_errors(self, view, errors, lines, errorUnderlines,
                     violationUnderlines, warningUnderlines, errorMessages,
                     violationMessages, warningMessages):

        for line in errors.splitlines():
            match = re.match(
                r'(?:stdin,\d+,error,)?Error: Parse error on line (?P<line>\d+): (?P<error>.+)',
                line
            )
            if match == None:
                match = re.match(
                    r'stdin,(?P<line>\d+),(?P<type>[a-z]+),(?P<error>.*)',
                    line
                )
            if match == None:
                match = re.match(
                    r'Error: (?P<error>.+) on line (?P<line>\d+)',
                    line
                )

            if match:
                line_num, error_text = (
                    int(match.group('line')),
                    match.group('error'),
                )

                try:
                    error_type = match.group('type')
                except IndexError:
                    error_type = None

                self.add_message(
                    line_num,
                    lines,
                    error_text,
                    errorMessages if error_type == 'error' else warningMessages
                )

    def write_config_file(self):
        """
        coffeelint requires a config file to be able to pass configuration
        variables to the program. this function writes a configuration file to
        hold them and sets the location of the file
        """
        self.coffeelint_config_file = os.path.join(TEMPFILES_DIR, 'coffeelint.json')
        temp_file = open(self.coffeelint_config_file, 'w')
        temp_file.write(
            simplejson.dumps(
                self.coffeelint_config,
                separators=(',', ':')
            )
        )
        temp_file.close()
