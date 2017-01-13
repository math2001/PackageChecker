# -*- encoding: utf-8 -*-

from . import Checker
from functions import *
import py_compile

class CheckScripts(Checker):

    def run(self):
        for file in self.glob_files(extension='.py'):
            file = self.rel_path(file)
            try:
                py_compile.compile(self.abs_path(file), doraise=True)
            except py_compile.PyCompileError as e:
                e = e.args[2] # the actual SyntaxError
                self.fail('Syntax Error: File {!r}, line {!r}'.format(file, e.lineno),
                          e.text.replace('\n', ''),
                          ' ' * (e.offset - 2) + '^',
                          'Message: ' + e.msg)
