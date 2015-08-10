# -*- coding: utf-8 -*-

def enum(**enums):
    return type('Enum', (), enums)


def keyset_in_enum(enum_type):
    keys = []
    for key in enum_type.__dict__:
        if key.startswith('__'):
           continue
        keys.append(key)

    return keys


def value_in_enum(enum_type, key):
    return enum_type.__dict__[key]
