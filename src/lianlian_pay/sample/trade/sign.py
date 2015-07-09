# -*- coding: utf-8 -*-
from Crypto.Hash import MD5

def sign(target, sign_type, key):
    if target is None:
        return ''
    sign_item_serial = _serialize(target)
    if sign_type == 'MD5':
        return _md5_encrypt(sign_item_serial, key)
    raise Exception("Cannot handle sign types except MD5.")

def _serialize(target):
    sorted_items = sorted(target.items())
    candidates = []
    for item in sorted_items:
        key = item[0]
        value = item[1]
        if key.lower() == 'sign':
            continue
        if _is_empty(value):
            continue
        candidates.append(key + '=' + value)
    return '&'.join(candidates)

def _is_empty(string):
    return string == None or string.strip() == ''

def _append_key(string, key):
    return string + "&key=" + key

def _md5_encrypt(string, key):
    m = MD5.new()
    m.update(_append_key(string, key))
    return m.hexdigest()
