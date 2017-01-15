# -*- encoding: utf-8 -*-

import os.path
import glob
import json
from functions import *

CHECKERS = map(lambda item: os.path.splitext(os.path.basename(item))[0],
               glob.glob('checkers/check_*.py'))

class Checker:

    """Every checker inherits from this class.
    It implements every global function"""

    def __init__(self, path, infos, is_pull_request):
        self.path = path
        self.labels = infos.get('labels', [])
        self.name = infos.get('name', None)
        self.is_pull_request = is_pull_request

    @staticmethod
    def reset():
        Checker.fails = {}
        Checker.warns = {}

    def add_msg(self, type, msg, description):
        getattr(Checker, type).setdefault(name(self), []).append([msg, description])

    def fail(self, msg, *descriptions):
        self.add_msg('fails', msg, '\n'.join(descriptions))

    def warn(self, msg, *descriptions):
        self.add_msg('warns', msg, '\n'.join(descriptions))

    def abs_path(self, path):
        if path.startswith(os.path.sep):
            raise ValueError("Your path is relative to the tested package, wherever you are.")
        return os.path.join(self.path, path)

    def rel_path(self, path):
        """return relative path (from the package)"""
        path = path.replace(self.path, '')
        if path.startswith(os.path.sep):
            return path[1:]
        return path

    def is_file(self, file_name):
        return os.path.isfile(self.abs_path(file_name))

    def is_folder(self, path):
        return os.path.isfolder(self.abs_path(path))

    def get_file_content(self, file_name):
        with open(self.abs_path(file_name), 'r') as fp:
            return fp.read()

    def glob_folders(self, **kwargs):
        items = []
        base_path = os.path.join(self.path, kwargs.get('base_path', ''))
        def recursive(path, **kwargs):
            for item in os.listdir(path):
                if os.path.isdir(os.path.join(path, item)):
                    if kwargs.get('name', None) == item:
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
                elif 'extension' in kwargs \
                    and os.path.splitext(item)[1] == kwargs['extension']:
                    files.append(self.rel_path(os.path.join(path, item)))
                elif 'file_name' in kwargs and kwargs['file_name'] == item:
                    files.append(self.rel_path(item))
                elif 'rel_path' in kwargs and kwargs['rel_path'] == self.rel_path(item):
                    files.append(self.rel_path(item))
            return files

        return recursive(base_path, **kwargs)

    def get_static(self, path):
        if path.startswith(os.path.sep):
            raise ValueError("Your path is relative to this package, wherever you are.")
        return os.path.normpath(os.path.join(__file__, '..', '..', 'static', path))


    @staticmethod
    def output(format):
        if format == 'human':
            indentation = ' ' * 4

            def render(text, title, data):
                text.append('{} [{}]'.format(title, len(data)))
                text.append('*' * len(text[-1]))
                for trigger, packs in data.items():
                    text.append('')
                    text.append(indentation + trigger + ' [%i]' % len(packs))
                    text.append(indentation + '-' * len(text[-1].lstrip()))
                    for msg, description in packs:
                        text.append(indentation + msg)
                        for line in description.splitlines():
                            text.append(indentation * 2 + line)

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
            return json.dumps(result)

class FileChecker(Checker):

    def fail(self, msg, *descriptions):
        super().fail(msg, *list(descriptions) \
                          + ['- Found in {!r}'.format(self.current_file)])

    def warn(self, msg, *descriptions):
        super().warn(msg, *list(descriptions) \
                          + ['- Found in {!r}'.format(self.current_file)])
