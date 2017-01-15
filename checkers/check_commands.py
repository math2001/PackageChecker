# -*- encoding: utf-8 -*-

from . import FileChecker
from functions import *

class CheckCommands(FileChecker):

    """Check .sublime-commands files"""

    ALLOWED_KEYS = {
        'caption': "str",
        'command': "str",
        'args': "dict"
    }

    def check(self, content):
        try:
            items = json_parse(content)
        except ValueError as e:
            self.fail('Invalid JSON file',
                      "In {!r}".format(self.current_file)
                      "Trailing commas and comments aren't allowed.",
                      "Error message: {}".format(error))
            return

        for item in items:
            if not 'caption' in item:
                self.fail("Each item needs a 'caption' key",
                          "command specified: {!r}".format(item.get('command', 'None')))
            elif not 'command' in item:
                self.fail("Each item needs a 'command' key",
                          "caption specified: {!r}".format(item['caption']))
            for key, value in item.items():
                if key not in self.ALLOWED_KEYS:
                    self.fail("Found an unallowed key",
                              "The key is {!r}".format(key),
                              "caption specified: {!r}".format(item['caption']))
                elif name(value) != self.ALLOWED_KEYS[key]:
                    self.fail('Found an unexpected type',
                              'The value of the key {!r} should be a {!r}, got a {!r}'.format(key,
                                                            self.ALLOWED_KEYS[key], name(value)))
                elif key == 'args' and value == {}:
                    self.warn("You don't need to specify 'args' if you set it to '{}'")

    def run(self):
        for file in self.glob_files(extension='.sublime-commands'):
            file = self.rel_path(file)
            self.current_file = file
            self.check(self.get_file_content(self.abs_path(file)))
