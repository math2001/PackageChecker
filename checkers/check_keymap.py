# -*- encoding: utf-8 -*-

import json
import os.path
from . import Checker
from re import compile as re_comp
from functions import *
import jsonc

class CheckKeymap(Checker):

    MATCH_VALID_NAME = re_comp(r'^Default( \((Windows|Linux|OSX)\))?\.sublime-keymap$')

    ALLOWED_KEYS = {
        'keys': 'list',
        'context': 'list',
        'args': 'dict',
        'command': 'str',
        'key': 'str',
    }

    ALLOWED_CONTEXT_KEYS = {
        'match_all': 'bool',
        'operator': 'str',
        'operand': None,
        'key': 'str'
    }

    def fail(self, msg, *descriptions):
        super().fail(msg, *list(descriptions) \
                          + ['- Found in {!r}'.format(self.current_file)])

    def warn(self, msg, *descriptions):
        super().warn(msg, *list(descriptions) \
                          + ['- Found in {!r}'.format(self.current_file)])

    def compare_against(self, base, against):
        for base_binding in base:
            for ag_binding in against:
                pass


    def check_keymap_file(self, pck_keymaps, platform):
        """check that a keymap is valid AND doesn't overwrites the default ones
            @params:
                - pck_keymaps: a decoded JSON keymap file
                - platform: the platform to compare against (can be *)
        """
        bindings = {
            'Linux': jsonc.loads(self.get_file_content(self.get_static('Default (Linux).sublime-keymap'))),
            'Windows': jsonc.loads(self.get_file_content(self.get_static('Default (Windows).sublime-keymap'))),
            'OSX': jsonc.loads(self.get_file_content(self.get_static('Default (OSX).sublime-keymap')))
        }

        if platform == '*':
            platforms = ['Linux', 'Windows', 'OSX']
        else:
            platforms = [platform]

        for binding in pck_keymaps:
            for pck_key, pck_value in binding.items():
                if pck_key not in self.ALLOWED_KEYS:
                    self.fail("Found an unallowed key",
                              "The key is {!r}".format(pck_key))
                elif type(pck_value).__name__ != self.ALLOWED_KEYS[pck_key]:
                    self.fail('Found an unallowed value for the key {!r}'.format(pck_key),
                              "Expected a {!r}, got a {!r}".format(self.ALLOWED_KEYS[pck_key],
                                                                   type(pck_value).__name__))
                if pck_key == 'context':
                    for condition in binding['context']:
                        for ctx_key, ctx_value in condition.items():
                            if ctx_key not in self.ALLOWED_CONTEXT_KEYS:
                                self.fail('Found an unallowed context key',
                                          'The key is {!r}'.format(ctx_key))
                            elif self.ALLOWED_CONTEXT_KEYS[ctx_key] is not None \
                                and type(ctx_value).__name__ != self.ALLOWED_CONTEXT_KEYS[ctx_key]:
                                self.fail('Found an unallowed value for the context key '
                                          + repr(ctx_key), "Expected a {!r}, got a {!r}".format(
                                                                 self.ALLOWED_CONTEXT_KEYS[ctx_key],
                                                                 type(ctx_value).__name__))

            if 'keys' not in binding:
                self.fail("A key binding needs a 'keys' key. Didn't find any.")
            if 'command' not in binding:
                self.fail("A key binding needs a 'commands' key. Didn't find any.")

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
                            self.fail('Overwrites the {} default bindings unconditionally'.format(platform),
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
