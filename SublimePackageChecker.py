# -*- encoding: utf-8 -*-

"""
This script provides an interface of PackageChecker for Sublime Text 3
"""

import sys
import os.path
import sublime
from sublime_plugin import WindowCommand

sys.path.append(os.path.join(os.path.dirname(__file__)))
from .PackageChecker import check, parse_args
sys.path.pop()

class PackageCheckerCommand(WindowCommand):

    def run(self):
        # return
        self.window.show_input_panel('$ PackageChecker.py ', 'C:/python/package_control/sample_packages/scripts', self.run_command, None, None)

    def run_command(self, args):
        output = check(parse_args(args.split(' ')))
        output_panel = self.window.create_output_panel('PackageChecker')
        output_panel.run_command('append', {'characters': output})
        self.window.run_command('show_panel', {'panel': 'output.PackageChecker'})
