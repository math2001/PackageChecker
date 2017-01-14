# -*- encoding: utf-8 -*-

# Check the package name (not sublime in it, etc)

from . import Checker
from functions import *
from re import compile as re_comp

class CheckPackageName(Checker):

    RECOMMENDED_NAME = re_comp(r'[ -~]')

    FORBIDDEN_SIGNS = '.<>:"/\\|?*'

    def run(self):
        if not self.is_pull_request:
            return

        if 'sublime' in self.name.lower() or 'st' in self.name.lower():
            self.warn("There shouldn't be 'sublime' in your package name.",
                      "Every package here *are* for Sublime Text, so no need to specify it again")

        for forbidden_sign in self.FORBIDDEN_SIGNS:
            if forbidden_sign in self.name:
                self.fail("The sign {!r} isn't allowed in packages' name".format(forbidden_sign))

        if not RECOMMENDED_NAME.match(self.name):
            self.warn('Your package name should be composed exclusively by ASCII characters')
