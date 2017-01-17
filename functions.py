# -*- encoding: utf-8 -*-
from re import compile as re_comp
from json import JSONDecoder
import textwrap
import errno
import os
import stat

__all__ = ('is_valid_command_name', 'json_parse', 'to_camel_case', 'name', 'pep_print',
          'handle_remove_readonly', 'every')

MATCH_COMMAND_NAME = re_comp('^[a-z][a-z0-9_]+$')
json_decoder = JSONDecoder()

def is_valid_command_name(command):
    return MATCH_COMMAND_NAME.match(command) is not None

def json_parse(json):
    return json_decoder.decode(json)

def to_camel_case(string):
    return ''.join([bit.title() for bit in string.split('_')])

def name(obj):
    return type(obj).__name__

def pep_print(*args, **kwargs):
    # CSW: ignore
    print('\n'.join(textwrap.wrap(kwargs.get('sep', ' ').join(args), 79)), end=kwargs.get('end'))
    for i in range(kwargs.get('newlines', 0)):
        # CSW: ignore
        print()

def handle_remove_readonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
        func(path)
    else:
        raise

def every(iterable, func):
    for item in iterable:
        if not func(item):
            return False, item
    return True, None
