# -*- encoding: utf-8 -*-

import os
import argparse
import importlib
import sys
import subprocess
import tempfile

try:
    # for Sublime Text, not implemented for now
    from .checkers import CHECKERS
    from .get_package_infos import get_package_infos
    from .functions import *
except SystemError:
    # building
    from checkers import CHECKERS
    from get_package_infos import get_package_infos
    from functions import *

# NEEDS git on your system

__all__ = 'check',

def clone(tempdir, url, quiet):
    name = os.path.basename(url)
    if os.path.exists(os.path.join(tempdir, name)):
        # CSW: ignore
        if not quiet: print('Already cloned. Using it again')
        return os.path.join(tempdir, name)
    # CSW: ignore
    if not quiet: print('Cloning {} into {!r}'.format(url, name))
    cmd = ['git', 'clone', '--depth=1', '--branch=master', url, name]
    cmd = subprocess.Popen(cmd, cwd=tempdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # CSW: ignore
    if not quiet: print(cmd.stdout.read().decode())
    return os.path.join(tempdir, name)


def check(path, is_pull_request, quiet):

    tempdir = tempfile.gettempdir()

    tempdir = os.path.join(tempdir, 'SublimeTextPackageChecker')
    if not os.path.exists(tempdir):
        os.makedirs(tempdir)
    elif os.path.isfile(tempdir):
        raise OSError('The tempdir is a file. Please remove {!r}'.format(tempdir))

    infos = {}
    if is_pull_request:
        infos = get_package_infos(path)
        path = clone(tempdir, infos['details'], quiet)
    elif path.startswith(('https://', 'http://')):
        path = clone(tempdir, path, quiet)

    path = os.path.normpath(path)

    for checker_name in CHECKERS:
        module = importlib.import_module('.check_' + checker_name,
                                         package="checkers")
        Checker = getattr(module, 'Check' + to_camel_case(checker_name))
        Checker(path, infos).run()

    Checker.output()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="PackageChecker", description="Check your Sublime Text "
                                                                        "Packages really simply")
    parser.add_argument('path', help='Path (or URL) to the package to check.')
    parser.add_argument('-p', '--pull-request', action='store_true', help="It's a URL to a pull "
                                                                          "request")
    parser.add_argument('-q', '--quiet', action="store_true", help='Output the strict minimum '
                                                                   '(fails and warning)')
    parser.add_argument('-i', '--interactive', action='store_true', help="Run the test "
                            "interactively. If specified, you shouldn't specify *any* other "
                            "argument")
    args = parser.parse_args()
    # CSW: ignore
    print("PackageChecker.py", 'overwrite args: remove the list when in production\n')
    check(args.path, args.pull_request, args.quiet)
