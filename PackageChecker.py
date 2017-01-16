# -*- encoding: utf-8 -*-

import os
import argparse
import importlib
import sys
import subprocess
import tempfile
import textwrap

sys.path.append(os.path.join(os.path.dirname(__file__)))

try:
    from .checkers import CHECKERS
    from .get_package_infos import get_package_infos
    from .functions import *
    from .constants import *
except SystemError:
    from checkers import CHECKERS
    from get_package_infos import get_package_infos
    from functions import *
    from constants import *

sys.path.pop()

# NEEDS git on your system

def clone(url, quiet):
    name = os.path.basename(url)
    if os.path.exists(os.path.join(TEMP_DIR, name)):
        # CSW: ignore
        if not quiet: print('Already cloned. Using {} again'.format(os.path.join(TEMP_DIR, name)))
        return os.path.join(TEMP_DIR, name)
    # CSW: ignore
    if not quiet: print('Cloning {} into {!r}'.format(url, name))
    cmd = ['git', 'clone', '--depth=1', '--branch=master', url, name]
    cmd = subprocess.Popen(cmd, cwd=TEMP_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # CSW: ignore
    if not quiet: print(cmd.stdout.read().decode())
    return os.path.join(TEMP_DIR, name)


def check(args):

    path = args.path
    is_pull_request = args.pull_request
    quiet = args.quiet
    ignored_checkers = args.ignore
    format = 'json' if args.json else 'human'

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
        path = clone(infos['details'], quiet)
    elif path.startswith(('https://', 'http://')):
        path = clone(path, quiet)

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

    return Checker.output(format=format)

def parse_args(args=None):
    parser = argparse.ArgumentParser(prog="PackageChecker",
                                     description="Check your Sublime Text Packages really simply",
                                     fromfile_prefix_chars='@')
    parser.add_argument('path', nargs="?", help='Path (or URL) to the package to check.')
    parser.add_argument('-p', '--pull-request', action='store_true', help="It's a URL to a pull "
                                                                          "request")
    parser.add_argument('-q', '--quiet', action="store_true", help='Output the strict minimum '
                                                                   '(fails and warning)')
    parser.add_argument('-j', '--json', action='store_true', help='Output the result in a JSON '
                                                                  'format.')
    parser.add_argument('-i', '--interactive', action='store_true', help="Run the test "
                            "interactively. If specified, you shouldn't specify *any* other "
                            "argument")
    parser.add_argument('-x', '--ignore', action='append', metavar="CK", default=[], help="Exclude "
                                    "the entire checker. You can specify this option several times")
    return parser.parse_args(args), parser

if __name__ == '__main__':
    # it's run from the command line
    args, parser = parse_args()

    if args.interactive and (args.pull_request is True or
                             args.quiet is True or args.path is not None):
        # CSW: ignore
        pep_print("Interactive mode overwrites every other settings. So, you can't specify any other "
              "options if you choose interactive mode", newlines=1)
        parser.print_help()
        exit(1)

    if args.interactive:
        if sys.version_info.major == 3:
            ask = input
        elif sys.version_info.major == 2:
            ask = raw_input
        else:
            raise SystemError('Unknown version of python. Please update')

        def confirm(msg):
            ans = ask(msg)
            if ans.lower() in ('y', 'yes'):
                return True
            elif ans.lower() in ('n', 'no'):
                return False
            else:
                return confirm(msg)

        args.path = ask('Path or URL> ')
        args.quiet = confirm('quiet (y/n)> ')
        args.pull_request = confirm('is a pull request (y/n)> ')
        args.json = confirm('Output in a JSON format (y/n)> ')

    if args.path is None or args.path == '':
        pep_print('FATAL: You need to specifiy a path (got {!r})'.format(args.path))
        exit(1)

    # CSW: ignore
    print(check(args))
