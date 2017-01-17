# -*- encoding: utf-8 -*-

import os.path
import glob
import json
from functions import *
import jsonc
import textwrap

CHECKERS = map(lambda item: os.path.splitext(os.path.basename(item))[0],
               glob.glob('checkers/check_*.py'))

class Checker:

    """Every checker inherits from this class.
    It implements every global function"""

    ALLOWED_KEYS_FOR_MSG = ('file', )

    def __init__(self, path, infos, is_pull_request):
        self.path = path
        self.labels = infos.get('labels', [])
        self.name = infos.get('name')
        self.is_pull_request = is_pull_request
        self.support_st2 = infos.get('support_st2', False)

    @staticmethod
    def reset():
        Checker.fails = {}
        Checker.warns = {}

    def add_msg(self, type, msg, description, **kwargs):
        if 'description' in kwargs:
            raise ValueError("You shouldn't include 'description' in kwargs. See the dev part in the "
                             "wiki")
        valid, key = every(kwargs.keys(), lambda key: key in Checker.ALLOWED_KEYS_FOR_MSG)
        if not valid:
            raise ValueError("The key {!r} isn't allowed. See the dev part in the wiki".format(key))

        kwargs['description'] = description
        file = kwargs.get('file', '')
        dict = getattr(Checker, type) \
            .setdefault(name(self), {}) \
            .setdefault(msg, {}) \
            .setdefault(file, []).append(description)


    def fail(self, msg, *descriptions, **kwargs):
        self.add_msg('fails', msg, '\n'.join(descriptions), **kwargs)

    def warn(self, msg, *descriptions, **kwargs):
        self.add_msg('warns', msg, '\n'.join(descriptions), **kwargs)

    def abs_path(self, path=None):
        if path is None:
            return self.path
        if path.startswith(os.path.sep):
            raise ValueError("Your path is relative to the tested package, wherever you are.")
        return os.path.join(self.path, path)

    def rel_path(self, path):
        """return relative path (from the package)"""
        path = os.path.normpath(path)
        path = path.replace(self.path, '')
        if path.startswith(os.path.sep):
            return path[1:]
        return path

    def is_file(self, file_name):
        return os.path.isfile(self.abs_path(file_name))

    def is_folder(self, path):
        return os.path.isdir(self.abs_path(path))

    def is_dir(self, path):
        """An alias for is_folder"""
        return self.is_folder(path)

    def get_file_content(self, file_name):
        with open(self.abs_path(file_name), 'r') as fp:
            return fp.read()

    def glob_folders(self, **kwargs):
        items = []
        base_path = os.path.join(self.path, kwargs.get('base_path', ''))
        def recursive(path, **kwargs):
            for item in os.listdir(path):
                if os.path.isdir(os.path.join(path, item)):
                    if kwargs.get('name') == item:
                        items.append(item)
                    recursive(os.path.join(path, item), **kwargs)
            return items

        return recursive(base_path, **kwargs)

    def glob_files(self, **kwargs):
        """Need to do a glob function (can't use glob to support ST's python)"""
        files = []
        base_path = os.path.join(self.path, kwargs.get('base_path', ''))
        def recursive(path, **kwargs):

            for item in os.listdir(path):
                if os.path.isdir(os.path.join(path, item)):
                    recursive(os.path.join(path, item), **kwargs)
                elif 'extension' in kwargs:
                    if os.path.splitext(item)[1] == kwargs['extension']:
                        files.append(self.rel_path(os.path.join(path, item)))
                elif 'file_name' in kwargs:
                    if kwargs['file_name'] == item:
                        files.append(self.rel_path(os.path.join(path, item)))
                elif 'rel_path' in kwargs:
                    if kwargs['rel_path'] == self.rel_path(os.path.join(path, item)):
                        files.append(self.rel_path(os.path.join(path, item)))
                else:
                    files.append(self.rel_path(os.path.join(path, item)))
            return files

        return recursive(base_path, **kwargs)

    def get_static(self, path):
        if path.startswith(os.path.sep):
            raise ValueError("Your path is relative to this package, wherever you are.")
        return os.path.normpath(os.path.join(__file__, '..', '..', 'static', path))

    def load_json(self, string):
        if self.support_st2:
            return json.loads(string)
        else:
            return jsonc.loads(string)

    @staticmethod
    def output(format):
        if format == 'human':
            original_indentation = ' ' * 4

            indentation = original_indentation

            def render(text, title, data):
                indentation = ' ' * 4
                text.append('{} [{}]'.format(title, len(data)))
                text.append('*' * len(text[-1]))
                for trigger, types in data.items():
                    text.append('')
                    text.append(indentation + trigger)
                    text.append(indentation + '=' * (len(text[-1]) - len(indentation)))
                    indentation = original_indentation * 2
                    for type_, infos in types.items():
                        text.append('')
                        text.append(indentation + type_)
                        text.append(indentation + '-' * (len(text[-1]) - len(indentation)))
                        for file, descriptions in infos.items():
                            if file:
                                text.append(indentation + "> In '%s'" % file)
                            for description in descriptions:
                                text.append(textwrap.indent(description,
                                                indentation + original_indentation if file else ''))
                    indentation = original_indentation


            text = []
            render(text, 'Failer', Checker.fails)
            text.append('')
            render(text, 'Warners', Checker.warns)
            text += ['', 'This package shows you commons errors. To learn how to get '
                          'rid of them, please refer to the wiki']

            return '\n'.join(text)
        else:
            result = {
                'fails': Checker.fails,
                'warning': Checker.warns
            }
            return json.dumps(result, indent=4)

class FileChecker(Checker):

    def fail(self, msg, *descriptions):
        super().fail(msg, *list(descriptions), file=self.current_file)

    def warn(self, msg, *descriptions):
        super().warn(msg, *list(descriptions), file=self.current_file)
