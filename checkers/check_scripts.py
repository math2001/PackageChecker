# -*- encoding: utf-8 -*-

from . import Checker
from functions import *
from constants import TEMP_DIR
import py_compile
import os.path

class CheckScripts(Checker):

    def run(self):
        cfiledir = os.path.join(TEMP_DIR, '__SUBLIME_PACKAGE_CHECKER_PYCACHE')
        if not os.path.exists(cfiledir):
            os.makedirs(cfiledir)

        for file in self.glob_files(extension='.py'):
            cfile = os.path.join(cfiledir, os.path.splitext(file)[0] + '.pyc')
            file = self.rel_path(file)
            try:
                py_compile.compile(self.abs_path(file), doraise=True, cfile=cfile)
            except py_compile.PyCompileError as e:
                e = e.args[2] # the actual SyntaxError
                self.fail('Syntax Error: File {!r}, line {!r}'.format(file, e.lineno),
                        e.text.replace('\n', ''), ' ' * (e.offset - 2) + '^', 'Message: ' + e.msg)
