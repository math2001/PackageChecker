# -*- encoding: utf-8 -*-
from re import compile as re_comp

__all__ = ['is_valid_command_name']

MATCH_COMMAND_NAME = re_comp('^[a-z][a-z0-9_]+$')

def is_valid_command_name(command):
    return MATCH_COMMAND_NAME.match(command) is not None
