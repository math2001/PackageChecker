# -*- encoding: utf-8 -*-

"""
This script provides an interface of PackageChecker for Sublime Text 3
"""

import sys
import os.path
import shlex
import sublime
from sublime_plugin import WindowCommand
import traceback

sys.path.append(os.path.join(os.path.dirname(__file__)))
from .PackageChecker import check, parse_args
sys.path.pop()

class FakeFile:

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
        self.window.show_input_panel('$ PackageChecker.py ', '"C:/python/package_control/sample_packages/interface" -m -c', self.run_command, None, None)

    def run_command(self, args):
        real_stdout = sys.stdout
        real_stderr = sys.stderr
        sys.stdout = FakeFile()
        sys.stderr = FakeFile()
        try:
            output = str(check(parse_args(shlex.split(args))[0]))
        except SystemExit as e:
            output = sys.stdout.read() + '\n'
            output += sys.stderr.read() + '\n'
            output += 'system exited with {}'.format(e)
        except Exception as e:
            sys.stderr = real_stderr
            sys.stdout = real_stdout
            output = traceback.format_exc()
        finally:
            sys.stderr = real_stderr
            sys.stdout = real_stdout

        output_panel = self.window.create_output_panel('PackageChecker')
        output_panel.run_command('append', {'characters': output})
        self.window.run_command('show_panel', {'panel': 'output.PackageChecker'})
