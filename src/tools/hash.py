# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import hashlib
import hmac
from encoding import *


def hash_password(password):
    return _get_hmac(password, strong=True)


def _get_hmac(*parts, **kwargs):
    strong = kwargs.pop('strong', True)
    digestmod = hashlib.sha256 if strong else hashlib.sha1
    msg = '|'.join([unicode(part) for part in parts])
    return hmac.new(to_str(_get_hash_salt()), to_str(msg), digestmod).hexdigest()


def _get_hash_salt():
    return 'lvye'
