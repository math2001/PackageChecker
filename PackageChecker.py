# -*- encoding: utf-8 -*-

import os
import argparse
import importlib
import sys
import subprocess
import tempfile
import shutil


sys.path.append(os.path.join(os.path.dirname(__file__)))

try:
    from .checkers import CHECKERS
    from .get_package_infos import get_package_infos
    from .functions import *
    from .constants import *
    from .pyperclip import copy as pyperclip_sublime_copy
except SystemError:
    from checkers import CHECKERS
    from get_package_infos import get_package_infos
    from functions import *
    from constants import *
    from pyperclip import copy as pyperclip_sublime_copy

sys.path.pop()

# NEEDS git on your system

def clone(url, quiet, fresh):
    name = os.path.basename(url)
    path = os.path.join(TEMP_DIR, name)
    if os.path.exists(path):
        if fresh:
            if not quiet: pep_print("Clearing cache '{}'".format(path))
            shutil.rmtree(path, ignore_errors=False, onerror=handle_remove_readonly)
        else:
            if not quiet: pep_print("Already cloned. Using '{}' again".format(path))
            return path
    if not quiet: pep_print('Cloning {!r} into {!r}'.format(url, name))
    depth = '--depth=%i' % args.depth if args.depth else ''
    cmd = ['git', 'clone', depth, '--branch=master', '--verbose', url, name]
    cmd = subprocess.Popen(cmd, cwd=TEMP_DIR, stdout=subprocess.PIPE)
    if not quiet: pep_print(cmd.stdout.read().decode())
    return path

def check(args):

    path = args.path
    fresh = args.fresh
    quiet = args.quiet
    output_format = 'json' if args.json else 'markdown' if args.markdown else 'terminal'
    is_pull_request = args.pull_request
    ignored_checkers = args.ignore

    if len(ignored_checkers) > 0:
        # CSW: ignore
        print('Excluding the following checkers:',
              ', '.join([repr(ignored_checker) for ignored_checker in ignored_checkers]))

    ignored_checkers = list(map(lambda item: 'check_' + item, ignored_checkers))

    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    elif os.path.isfile(TEMP_DIR):
        raise OSError('The temp dir is a file. Please remove {!r}'.format(TEMP_DIR))

    infos = {}
    if is_pull_request:
        infos = get_package_infos(path)
        path = clone(infos['details'], quiet, fresh)
    elif path.startswith(('https://', 'http://')):
        path = clone(path, quiet, fresh)
        infos['support_st2'] = args.support_st2
        infos['depth'] = args.depth

    path = os.path.normpath(path)

    sys.path.append(os.path.join(os.path.dirname(__file__)))
    reset = True
    for checker_name in CHECKERS:
        if checker_name in ignored_checkers:
            continue
        try:
            # when run from Sublime Text
            module = importlib.import_module('.' + checker_name, package="PackageChecker.checkers")
        except SystemError:
            # when run from the terminal
            module = importlib.import_module('.' + checker_name, package="checkers")
        Checker = getattr(module, to_camel_case(checker_name))
        if reset:
            Checker.reset()
            reset = False
        Checker(path, infos, is_pull_request).run()

    sys.path.pop()

    return Checker.output(format=output_format)

def parse_args(args=None):
    parser = argparse.ArgumentParser(prog="PackageChecker",
                                     description="Check your Sublime Text Packages really simply",
                                     fromfile_prefix_chars='@')

    parser.add_argument('path', nargs="?", help='Path (or URL) to the package to check.')
    parser.add_argument('-p', '--pull-request', action='store_true', help="It's a URL to a pull "
                                                                          "request")
    parser.add_argument('-q', '--quiet', action="store_true", help='Output the strict minimum '
                                                                   '(fails and warning)')
    parser.add_argument('-i', '--interactive', action='store_true', help="Run the test "
                            "interactively. If specified, you shouldn't specify *any* other "
                            "argument")
    parser.add_argument('-x', '--ignore', action='append', metavar="CK", default=[], help="Exclude "
                                    "the entire checker. You can specify this option several times")
    parser.add_argument('-f', '--fresh', action='store_true', help="Don't use the cache")
    parser.add_argument('-b', '--support-st2', action='store_true', help='Backward compatible (for '
                                                                         'ST2)')
    parser.add_argument('-d', '--depth', metavar='DP', type=int, default=50, help="The "
                            "depth to clone the repo with. Only useful if it is a remote package")
    parser.add_argument('-c', '--clip', action='store_true', help='Copy the output to the clipboard'
                                                                                                   )
    format_group = parser.add_mutually_exclusive_group()
    format_group.add_argument('-j', '--json', action='store_true', help='Output the result in a '
                                                                        'JSON format.')
    format_group.add_argument('-m', '--markdown', action='store_true', help='Output the result in '
                                                                            'Markdown format.')

    return parser.parse_args(args), parser

if __name__ == '__main__':
    # it's run from the command line
    args, parser = parse_args()

    if args.interactive:
        args.path = ''
        while args.path == '':
            args.path = ask('Path or URL> ')
        args.quiet = confirm('quiet (y/n)> ')
        args.pull_request = confirm('is a pull request (y/n)> ')
        args.json = confirm('Output in a JSON format (y/n)> ')
        args.ignore = [checker.strip() for checkre in ask('ignore (comma separated)> ').split(',')]
        args.fresh = confirm('Fresh (y/n)> ')
        args.support_st2 = confirm('Support ST2 (y/n)> ')
        args.depth = int(ask('Depth {integer}> '))

    while not args.path:
        args.path = ask('Path or URL> ')

    output = check(args)
    if args.clip:
        if pyperclip_sublime_copy:
            pyperclip_sublime_copy(output)
        else:
            # CSW: ignore
            print("Copy functionality unavailable!")
    # CSW: ignore
    print(output)
