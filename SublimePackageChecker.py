# -*- encoding: utf-8 -*-

"""
This script provides an interface of PackageChecker for Sublime Text 3
"""

import sys
import os.path
import sublime
from sublime_plugin import WindowCommand
import sys

sys.path.append(os.path.join(os.path.dirname(__file__)))
from .PackageChecker import check, parse_args
sys.path.pop()

class FakeStdout:

    """Use to capture the output"""

    def __init__(self):
        self.file = ''

    def write(self, text):
        self.file += text

    def flush(self):
        pass

    def read(self):
        return self.file

class PackageCheckerCommand(WindowCommand):

    def run(self):
        self.window.show_input_panel('$ PackageChecker.py ', '--help', self.run_command, None, None)

    def run_command(self, args):
        real_stdout = sys.stdout
        sys.stdout = FakeStdout()
        try:
            output = str(check(parse_args(args.split(' '))))
        except SystemExit as e:
            output = sys.stdout.read()
            output += 'system exited with {}'.format(e)
        sys.stdout = real_stdout
        output_panel = self.window.create_output_panel('PackageChecker')
        output_panel.run_command('append', {'characters': output})
        self.window.run_command('show_panel', {'panel': 'output.PackageChecker'})
