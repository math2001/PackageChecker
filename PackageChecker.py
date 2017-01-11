# -*- encoding: utf-8 -*-

import os
import argparse
import importlib

from checkers import CHECKERS

parser = argparse.ArgumentParser()
parser.add_argument('package_path', help='You package to check.')
parser.add_argument('--st2', action='store_true', help="Is compatible with"
                                                        "Sublime Text 2")
args = parser.parse_args()

def to_camel_case(string):
    return ''.join([bit.title() for bit in string.split('_')])

for checker_name in CHECKERS:
    module = importlib.import_module('.check_' + checker_name,
                                     package="checkers")
    Checker = getattr(module, 'Check' + to_camel_case(checker_name))
    Checker(args.package_path, ['color scheme']).run()

Checker.output()
