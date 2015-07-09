# coding=utf-8
from __future__ import print_function, unicode_literals
import hashlib

def hmac_sign(avalue, akey, encode="UTF-8"):
    """
    对报文采用md5进行hmac签名
    :param value: 字符
    :param key: 密钥
    :param encode: 字符串编码方式
    :return: 签名结果, hex字符
    """
    keyb = akey.encode(encode)
    value = avalue.encode(encode)

    k_ipad = [chr(54)] * 64
    k_opad = [chr(92)] * 64
    for i, c in enumerate(keyb):
        k_ipad[i] = chr(ord(c) ^ 0x36)
        k_opad[i] = chr(ord(c) ^ 0x5c)
    k_ipad = ''.join(k_ipad)
    k_opad = ''.join(k_opad)

    md = hashlib.md5()

    md.update(k_ipad)
    md.update(value)
    dg = md.digest()

    md = hashlib.md5()
    md.update(k_opad)
    md.update(dg[:16])

    return md.hexdigest()
