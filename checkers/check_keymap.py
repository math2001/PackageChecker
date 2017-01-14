# -*- encoding: utf-8 -*-

import json
import os.path
from . import FileChecker
from re import compile as re_comp
from functions import *
import jsonc

class CheckKeymap(FileChecker):

    MATCH_VALID_NAME = re_comp(r'^Default( \((Windows|Linux|OSX)\))?\.sublime-keymap$')

    ALLOWED_KEYS = {
        'keys': 'list',
        'context': 'list',
        'args': 'dict',
        'command': 'str',
    }

    ALLOWED_CONTEXT_KEYS = {
        'match_all': 'bool',
        'operator': 'str',
        'operand': None,
        'key': 'str'
    }

    def check_keys(self, keys):
        """Needs to be improved
            @params:
                - keys: ["ctrl+a", "alt+b"]
        """
        if not isinstance(keys, list):
            self.fail('Keys must be a *list* of non-empty strings',
                      "Got a {!r}".format(name(keys)))

        for bit in keys:
            if not isinstance(bit, str):
                self.fail('Keys must be a list of non-empty *strings*',
                          "Got a {!r}".format(name(bit)))
            elif name == '':
                self.fail('Keys must be a list of *non-empty* strings')
            elif name in ['ctrl', 'alt', 'super', 'shift']:
                self.fail('Sublime Text does not allow modifiers alone to be a valid combination')


    def check_keymap_file(self, pck_keymaps, platform):
        """check that a keymap is valid AND doesn't overwrites the default ones
            @params:
                - pck_keymaps: a decoded JSON keymap file
                - platform: the platform to compare against (can be *)
        """
        if not isinstance(pck_keymaps, list):
            return self.fail('Keymaps must be lists. Got {!r} instead'.format(name(pck_keymaps)))

        if platform == '*':
            platforms = ['Linux', 'Windows', 'OSX']
        else:
            platforms = [platform]

        bindings = {
            'Linux': jsonc.loads(
                self.get_file_content(self.get_static('Default (Linux).sublime-keymap'))),
            'Windows': jsonc.loads(
                self.get_file_content(self.get_static('Default (Windows).sublime-keymap'))),
            'OSX': jsonc.loads(
                self.get_file_content(self.get_static('Default (OSX).sublime-keymap')))
        }

        for binding in pck_keymaps:
            for pck_key, pck_value in binding.items():
                if pck_key not in self.ALLOWED_KEYS:
                    self.fail("Found an unallowed key: {!r}".format(pck_key))
                elif name(pck_value) != self.ALLOWED_KEYS[pck_key]:
                    self.fail('Found an unallowed value for the key {!r}'.format(pck_key),
                              "Expected a {!r}, got a {!r}".format(self.ALLOWED_KEYS[pck_key],
                                                                   name(pck_value)))
                if pck_key == 'context':
                    for condition in binding['context']:
                        for ctx_key, ctx_value in condition.items():
                            if ctx_key not in self.ALLOWED_CONTEXT_KEYS:
                                self.fail('Found an unallowed context key',
                                          "{!r} isn't allowed".format(ctx_key))
                            elif self.ALLOWED_CONTEXT_KEYS[ctx_key] is not None \
                                and name(ctx_value) != self.ALLOWED_CONTEXT_KEYS[ctx_key]:
                                self.fail('Found an unallowed value for the context key '
                                          + repr(ctx_key), "Expected a {!r}, got a {!r}".format(
                                                                 self.ALLOWED_CONTEXT_KEYS[ctx_key],
                                                                 name(ctx_value)))

            if 'keys' not in binding:
                return self.fail("A key binding needs a 'keys' key. Didn't find any.")
            if 'command' not in binding:
                return self.fail("A key binding needs a 'commands' key. Didn't find any.")

            # even if it fails, there is no need to stop this function: it won't affect anything
            self.check_keys(binding['keys'])

            for platform in platforms:
                for default_binding in bindings[platform]:
                    if default_binding['keys'] == binding['keys'] \
                        and 'context' not in default_binding:
                        if 'context' in binding:
                            self.warn('Overwrites the {} default binding'.format(platform),
                                      'The keys are: {!r}'.format(binding['keys']),
                                      "Note that this there's a context, so be sure that it's "
                                      "working properly and you can ignore this warning",
                                      "The default command {!r} is overwritten by {!r}".format(
                                                                        default_binding['command'],
                                                                        binding['command']))


                        else:
                            self.fail('Overwrites the {} default bindings unconditionally'.format(
                                                                                          platform),
                                      'The keys are: {!r}'.format(binding['keys']),
                                      "The default command {!r} is overwritten by {!r}".format(
                                                                        default_binding['command'],
                                                                        binding['command']))


    def run(self):
        files = self.glob_files(extension='.sublime-keymap')
        for file in files:
            self.current_file = file
            file = os.path.basename(file)
            if not self.MATCH_VALID_NAME.search(file):
                self.fail('Invalid name for a keymap file.', 'Name: {}'.format(file))
                continue

            platform = '*'
            if 'Linux' in file: platform = 'Linux'
            if 'Windows' in file: platform = 'Windows'
            if 'OSX' in file: platform = 'OSX'
            self.check_keymap_file(jsonc.loads(self.get_file_content(self.current_file)), platform)
