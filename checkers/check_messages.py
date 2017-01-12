# -*- encoding: utf-8 -*-

from functions import *
from . import Checker

class CheckMessages(Checker):

    def run(self):
        if not self.is_file('messages.json'):
            self.warn("Your package should include a 'messages.json' file.")
            return

        try:
            messages = json_parse(self.get_file_content('messages.json'))
        except ValueError as e:
            self.fail("Parse error when loading 'message.json'",
                      "Error message: {}".format(e),
                      "Trailing commas and comments aren't allowed")
            return

        if not isinstance(messages, dict):
            self.fail("Invalid structure in 'messages.json'.",
                      "The parent should be a 'dict', got a {}".format(type(messages.__class__)))
            return

        if not 'install' in messages:
            self.warn("You 'messages.json' should include an 'install' key")

        for version, message_file in messages.items():
            if not self.is_file(message_file):
                self.fail("An unexisting message file has been specified",
                          "{!r} does not exists.".format(message_file))
