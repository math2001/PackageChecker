# -*- encoding: utf-8 -*-

from . import FileChecker
from functions import *

class CheckMenu(FileChecker):

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

    VALID_NAME = [
        'Main',
        'Context',
        'Encoding',
        'Find in Files',
        'Indentation',
        'Line Endings',
        'Side Bar Mount Point',
        'Side Bar',
        'Syntax',
        'Tab Context',
        'Widget Context'
    ]

    def check_menu(self, menu):
        """Check one menu: one object"""
        if 'children' in menu and 'command' in menu:
            self.warn("You shouldn't have a 'command' and 'children' key "
                      "in the same 'dict'.",
                      "The caption for this item is {!r}".format(menu.get('caption',
                                                                          '<not specified>')))
        elif 'children' not in menu and 'command' not in menu and menu.get('caption', None) != '-':
            self.warn("Each 'dict' should have a 'command' or 'children' key.")

        for key, value in menu.items():
            # run value specific tests
            if key not in self.ALLOWED_KEYS.keys():
                self.fail('An unallowed key has been found',
                    'The key is {!r} and has for value {!r}'.format(key, value),
                    "Note: the key's are case sensitive")
            elif name(value) != self.ALLOWED_KEYS[key]:
                self.fail('Found an unexpected type',
                          'For the key {!r}, excepted a {!r}, got a {!r}'.format(key,
                                                               self.ALLOWED_KEYS[key], name(value)))
            elif key == 'children':
                self.check_menus(menu['children'])

    def check_menus(self, menus):
        if not isinstance(menus, list):
            self.fail('Menus should be a list',
                      'Got an {} in the file {}'.format(name(menu)))
            return
        for menu in menus:
            self.check_menu(menu)

    def run(self):
        for file in self.glob_files(extension='.sublime-menu'):
            self.current_file = self.rel_path(file)
            try:
                menus = json_parse(self.get_file_content(file))
            except ValueError as error:
                self.fail('Invalid JSON file',
                          "In '{}'".format(self.current_file),
                          "Trailing commas and comments aren't allowed.",
                          "Error message: {}".format(error))
            else:
                self.check_menus(menus)
