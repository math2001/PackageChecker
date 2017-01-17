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
                      "In {!r}".format(self.current_file),
                      "Error message: {}".format(error))
            return

        for item in items:
            if not 'caption' in item:
                self.fail("Each item needs a 'caption' key",
                          "command specified: {!r}".format(item.get('command', 'None')))
            elif not 'command' in item:
                self.fail("Each item needs a 'command' key",
                          "Caption specified: {!r}".format(item['caption']))
            for key, value in item.items():
                if key not in self.ALLOWED_KEYS:
                    self.fail("Found unallowed key(s)",
                              "The key is {!r}. Caption specified {!r}".format(key,
                                                                               item.get('caption')))
                elif name(value) != self.ALLOWED_KEYS[key]:
                    self.fail('Found an unexpected type',
                              'The value of the key {!r} should be a {!r}, got a {!r}'.format(key,
                                                            self.ALLOWED_KEYS[key], name(value)))
                elif key == 'args' and value == {}:
                    self.warn("You don't need to specify 'args' if you set it to '{}'",
                              "Caption specified: {!r}. Command specified: {!r}".format(
                                                          item.get('caption')), item.get('command'))

    def run(self):
        for file in self.glob_files(extension='.sublime-commands'):
            file = self.rel_path(file)
            self.current_file = file
            self.check(self.get_file_content(self.abs_path(file)))
