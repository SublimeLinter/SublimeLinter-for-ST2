# -*- coding: utf-8 -*-
# coffeescript.py - sublimelint package for checking coffee files
# inspired by https://github.com/clutchski/coffeelint

import re
import os
from subprocess import Popen, PIPE, call

try:
    import simplejson
except ImportError:
    import json as simplejson

from base_linter import BaseLinter, TEMPFILES_DIR

    #if an exception wasn't raised by the call, then coffeelint is ok
#    CONFIG = {
#        'executable': 'coffeelint.cmd' if os.name == 'nt' else 'coffeelint',
#        'lint_args': ['--stdin', '--nocolor', '--csv'],
#    }
#except:
    #fallback on the regualar coffee command
#    CONFIG = {
#        'executable': 'coffee.cmd' if os.name == 'nt' else 'coffee',
#        'lint_args': ['-s', '-l'],
#    }

CONFIG = {'language': 'CoffeeScript'}


def write_config_file(config):
    """
    coffeelint requires a config file to be able to pass configuration
    variables to the program. this function writes a configuration file to
    hold them and returns the location of the file
    """
    temp_file_name = os.path.join(TEMPFILES_DIR, 'coffeelint.json')
    temp_file = open(temp_file_name, 'w')
    temp_file.write(
        simplejson.dumps(config, separators=(',', ':'))
    )
    temp_file.close()
    return temp_file_name


class Linter(BaseLinter):
    def __init__(self, config):
        super(Linter, self).__init__(config)

        self.coffeelint_config = {}
        self.coffeelint_config_file = ''

        if os.name == 'nt':
            self.coffeelint_command, self.coffee_command = (
                'coffeelint.cmd',
                'coffee.cmd',
            )
        else:
            self.coffeelint_command, self.coffee_command = (
                'coffeelint',
                'coffee',
            )

        try:
            call(self.coffee_command)
            # will cause error if coffee is not installed
            self.coffee_enabled = True
        except:
            self.coffee_enabled = False

        try:
            call(self.coffeelint_command)
            # will cause error if coffeelint is not installed
            self.coffeelint_enabled = True
        except:
            self.coffeelint_enabled = False

    def get_executable(self, view):
        return (
            self.coffee_enabled,
            None,
            'built in' if self.coffee_enabled else 'the coffee command could not be used'
        )

    def built_in_check(self, view, code, filename):
        """
        this is overridden to allow both `coffee` and `coffeelint` to be used.
        as linters the return value is a tuple: [0] is the output from coffee
        and [1] is the output from coffeelint.
        """
        #check for config changes
        config = view.settings().get('coffeelint_options', {})

        if config != self.coffeelint_config:
            self.coffeelint_config = config
            self.coffeelint_config_file = write_config_file(self.coffeelint_config)

        if self.coffeelint_enabled:
            options = [
                self.coffeelint_command,
                '--stdin',
                '--nocolor',
                '--csv',
            ]

            if self.coffeelint_config != {}:
                options += ['--file', self.coffeelint_config_file]

            process = Popen(options, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            errors, stderrdata = process.communicate(code)  # send data to coffeelint binary
        else:
            # command to input coffee script via stdin and output errors via stdout
            process = Popen([self.coffee_command, '-s', '-l'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            stdoutdata, errors = process.communicate(code)  # send data to coffee binary

        return errors

    def parse_errors(self, view, errors, lines, errorUnderlines,
                     violationUnderlines, warningUnderlines, errorMessages,
                     violationMessages, warningMessages):

        for line in errors.splitlines():
            match = re.match(
                r'(?:stdin,1,error,)?Error: Parse error on line (?P<line>\d+): (?P<error>.+)',
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

                grp = errorMessages if error_type == 'error' else warningMessages
                self.add_message(line_num, lines, error_text, grp)
