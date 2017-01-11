# -*- encoding: utf-8 -*-

import os.path

CHECKERS = ['readme', 'menu']

class Checker:

    """Every checker inherits from this class.
    It implements every global function"""

    fails = {}
    warns = {}

    def __init__(self, path, labels):
        self.path = path
        self.labels = labels

    def add_msg(self, type, msg, description):
        getattr(Checker, type).setdefault(self.__class__.__name__, []).append([msg, description])

    def fail(self, msg, *descriptions):
        self.add_msg('fails', msg, '\n'.join(descriptions))

    def warn(self, msg, *descriptions):
        self.add_msg('warns', msg, '\n'.join(descriptions))

    def abs_path(self, path):
        if path.startswith(os.path.sep):
            raise ValueError('Your path is relative to this package, wherever'
                             "you are.")
        return os.path.join(self.path, path)

    def rel_path(self, path):
        """return relative path (from the package)"""
        path = path.replace(self.path, '')
        if path.startswith(os.path.sep):
            return path[1:]
        return path

    def has_file(self, file_name):
        return os.path.isfile(self.abs_path(file_name))

    def get_file_content(self, file_name):
        with open(self.abs_path(file_name), 'r') as fp:
            return fp.read()

    def glob_files(self, **kwargs):
        """Need to do a glob function (can't use glob to support ST's python)
        """
        files = []
        base_path = os.path.join(self.path, kwargs.get('base_path', ''))
        def recursive(path, **kwargs):

            for item in os.listdir(path):
                if os.path.isdir(os.path.join(path, item)):
                    recursive(os.path.join(path, item), **kwargs)

                elif kwargs.get('extension', None) is not None \
                    and os.path.splitext(item)[1] == kwargs['extension']:
                    files.append(self.rel_path(os.path.join(path, item)))
            return files

        return recursive(base_path, **kwargs)

    @staticmethod
    def output():
        indentation = ' ' * 4
        def render(text, title, data):
            text.append('{} ({})'.format(title, len(data)))
            text.append('*' * len(text[-1]))
            for trigger, packs in data.items():
                text.append(indentation + '> ' + trigger + ' (%i)' % len(packs))
                for msg, description in packs:
                    text.append(indentation + msg)
                    for line in description.splitlines():
                        text.append(indentation * 2 + line)

        text = []
        render(text, 'Failer', Checker.fails)
        text.append('')
        render(text, 'Warners', Checker.warns)

        # CSW: ignore
        print('\n'.join(text))
