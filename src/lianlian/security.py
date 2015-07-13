# coding=utf-8
from __future__ import unicode_literals
from hashlib import md5

def gen_sign_data(data):
    keys = data.keys()
    keys.sort(key=lambda x: x.lower())

    values = ['%s=%s' % (k, data[k]) for k in keys if k and k != 'sign']

    return '&'.join(values)


def sign_md5(data, key):
    src = gen_sign_data(data) + '&key=' + key
    return md5(src.encode('utf-8')).hexdigest()


def verify_md5(data, key):
    sign = data.get('sign')

    return sign == sign_md5(data, key)
