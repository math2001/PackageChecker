# -*- encoding: utf-8 -*-k

from re import compile as re_comp
from . import Checker
from constants import *


class CheckReadme(Checker):

    HAS_MARKDOWN_IMAGE = re_comp(r"!\[[^\\]*?\] *\(")

    def run(self):
        if not self.is_file('README.md'):
            return self.fail('Need a README.md for your package.')

        if 'color scheme' in self.labels \
            or 'theme' in self.labels \
            or self.glob_files(extension='.sublime-theme') \
            or self.glob_files(extension='.tmTheme'):
            if not CheckReadme.HAS_MARKDOWN_IMAGE.search(
                    self.get_file_content('README.md')):
                return self.warn("Because your package is a theme or a color scheme, it'd be "
                                 "better if you could add a demo in your README.md",
                                 "The valid format for an image in Markdown is "
                                 "![alt text](your/image/path). \nSee {} "
                                 "for more infos".format(MARKDOWN_CHEAT_SHEET))
