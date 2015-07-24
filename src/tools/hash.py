# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import hashlib
import hmac
from encoding import *
from top_config import config


def get_password_hash(password):
    return get_hmac(password, strong=True)


def get_hmac(*parts, **kwargs):
    strong = kwargs.pop('strong', True)
    digestmod = hashlib.sha256 if strong else hashlib.sha1
    msg = '|'.join([unicode(part) for part in parts])
    return hmac.new(to_str(get_hash_salt()), to_str(msg), digestmod).hexdigest()

def get_hash_salt():
    return config().get('app','hash_salt')