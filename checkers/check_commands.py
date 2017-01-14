# -*- encoding: utf-8 -*-

from . import Checker
from functions import *

class CheckCommands(Checker):

    """Check .sublime-commands files"""

    ALLOWED_KEYS = [
        'caption',
        'commands',
        'args'
    ]

    def check(self, content):
        try:
            items = json_parse(content)
        except ValueError as e:
            self.fail('Invalid JSON file'.format(self.current_file),
                      "Trailing commas and comments aren't allowed.",
                      "Error message: {}".format(error))
        else:
            for item in items:
                if not 'caption' in item:
                    self.fail("Each item needs a 'caption' key",
                              "command specified: {!r}".format(item.get('command', 'None')))
                elif not 'command' in item:
                    self.fail("Each item needs a 'command' key",
                              "caption specified: {!r}".format(item['caption']))
                for key, value in item.items():
                    if key not in self.ALLOWED_KEYS:
                        self.fail("The key '{}' is not allowed in those types of items",
                                  "caption specified: {!r}".format(item['caption']))
                    elif key == 'args' and value == {}:
                        self.warn("You don't need to specify 'args' if you set it to '{}'")

    def fail(self, msg, *descriptions):
        super().fail(msg, *list(descriptions) \
                          + ['- Found in {!r}'.format(self.current_file)])

    def warn(self, msg, *descriptions):
        super().warn(msg, *list(descriptions) \
                          + ['- Found in {!r}'.format(self.current_file)])

    def run(self):
        for file in self.glob_files(extension='.sublime-commands'):
            file = self.rel_path(file)
            self.current_file = file
            self.check(self.get_file_content(self.abs_path(file)))
