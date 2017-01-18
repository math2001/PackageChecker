# -*- encoding: utf-8 -*-

from . import Checker
from functions import *

class CheckTag(Checker):

    def run(self):
        if not self.is_folder('.git/refs/tags'):
            self.fail("Could not find the tags folder",
                      "You need to have initialized a git repository")
            return

        if len(self.glob_files(base_path='.git/refs/tags')) == 0:
            self.fail('You need to create at least one tag',
                      "Hasn't found any in the last {} commits".format(self.depth),
                      "Add --depth 0 to clone every commits (and --fresh to not use the cache)")
