# -*- encoding: utf-8 -*-

from . import Checker
from collections import OrderedDict
from json import JSONDecoder

json_decoder = JSONDecoder(object_pairs_hook=OrderedDict)

def json_parse(json):
    return json_decoder.decode(json)

class CheckMenu(Checker):

    ALLOWED_KEYS = {
        'mnemonic': 'str',
        'children': 'list',
        'id': 'str',
        'args': 'dict',
        'checkbox': 'bool',
        'caption': 'str',
        'platform': 'str',
        'command': 'str'
    }

    def check_menu(self, menu):
        """Check one menu: one object"""
        if 'children' in menu and 'command' in menu:
            self.warn("You shouldn't have a 'command' and 'children' key "
                      "in the same 'dict'.",
                      "The caption for this item is {!r}".format(menu.get('caption',
                                                                          '<not specified>')))
        elif 'caption' not in menu:
            self.warn("Each 'dict' should have a 'caption' key")
        elif 'children' not in menu and 'command' not in menu:
            self.warn("Each 'dict' should have a 'command' or 'children' key.")

        for key, value in menu.items():
            if key not in self.ALLOWED_KEYS.keys():
                self.fail('An unallowed key has been found',
                    'The key is {!r} and has for value {!r}'.format(key, value))
                return
            elif type(value).__name__ != self.ALLOWED_KEYS[key]:
                self.fail("The key '{}' isn't of the right type.".format(key),
                    "It should be a {}, got a {}".format(self.ALLOWED_KEYS[key],
                        type(value).__name__))
                return
            elif key == 'children':
                self.check_menus(menu['children'])



    def check_menus(self, menus):
        if not isinstance(menus, list):
            self.fail('Menus should be a list',
                      'Got an {} in the file {}'.format(type(menu).__name__))
            return
        for menu in menus:
            self.check_menu(menu)

    def fail(self, msg, *descriptions):
        super().fail(msg, *list(descriptions) \
                          + ['- Found in {!r}'.format(self.current_file)])
    def warn(self, msg, *descriptions):
        super().warn(msg, *list(descriptions) \
                          + ['- Found in {!r}'.format(self.current_file)])

    def run(self):
        for file in self.glob_files(extension='.sublime-menu'):
            self.current_file = self.rel_path(file)
            try:
                menus = json_parse(self.get_file_content(file))
            except ValueError as error:
                self.fail('The file "{}" is not a valid JSON file.'.format(self.current_file),
                          "Trailling commas and comments aren't allowed",
                          "Error message: {}".format(error))
            else:
                self.check_menus(menus)
