# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division


def to_str(s):
    if isinstance(s, (str, bytes)):
        return s
    if isinstance(s, unicode):
        return s.encode('utf-8')
    return str(s)


def to_unicode(s, encoding=None, remedial_encoding=None):
    if isinstance(s, unicode):
        return s
    if isinstance(s, (str, bytes)):
        encoding = encoding or 'utf-8'
        try:
            return unicode(s, encoding=encoding)
        except UnicodeDecodeError:
            if remedial_encoding and remedial_encoding != encoding:
                return unicode(s, encoding=remedial_encoding)
            else:
                raise
    return unicode(s)
