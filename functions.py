# -*- encoding: utf-8 -*-
from re import compile as re_comp
from json import JSONDecoder

__all__ = ['is_valid_command_name', 'json_parse', 'to_camel_case']

MATCH_COMMAND_NAME = re_comp('^[a-z][a-z0-9_]+$')
json_decoder = JSONDecoder()

def is_valid_command_name(command):
    return MATCH_COMMAND_NAME.match(command) is not None

def json_parse(json):
    return json_decoder.decode(json)

def to_camel_case(string):
    return ''.join([bit.title() for bit in string.split('_')])
