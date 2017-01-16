# -*- encoding: utf-8 -*-

from . import Checker
from functions import *

class CheckMetadata(Checker):

    def run(self):
        pyc = self.glob_files(extension='.pyc')
        if len(pyc) > 0:
            self.fail("Your package shouldn't include any .pyc files",
                    "Found {} of them".format(len(pyc)))

        pycache = self.glob_folders(name='__pycache__')
        if len(pycache):
            self.fail("Your package shouldn't include a __pycache__ folder",
                    "Found {} of them".format(len(pycache)))

        if self.is_file('package-metadata.json'):
            self.fail("Your package shouldn't include a 'package-metadata.json' file",
                    "Package Control will automatically create it for you")

        if self.is_file('.no-sublime-package'):
            if len(self.glob_files(extension='.py')):
                self.warn("Please make sure you need a '.no-sublime-package'.",
                          "This is just a warning because you might propose a python dependency")
            else:
                self.fail("You shouldn't need a '.no-sublime-package'",
                        "Please refer to the wiki to know how to manage without it")
