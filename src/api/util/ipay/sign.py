# coding=utf-8
from __future__ import unicode_literals
import base64
from hashlib import md5
from encrypt_utils import public_key
from .lianlian_config import config


def _gen_sign_data(data):
    keys = data.keys()
    keys.sort(key=lambda x: x.lower())

    values = ['%s=%s' % (k, data[k]) for k in keys if k and k != 'sign' and data[k]]

    return '&'.join(values)


def _sign_md5(src, key):
    src = src + '&key=' + key
    src = src.encode('utf-8')
    return md5(src).hexdigest()


def _sign_md5_data(data, key):
    src = _gen_sign_data(data)
    return _sign_md5(src, key)


def _verify_md5(src, key, signed):
    return signed == _sign_md5(src, key)


def _verify_md5_data(data, key):
    signed = data.get('sign')
    src = _gen_sign_data(data)

    return _verify_md5(src, key, signed)


def _sign_rsa(src, pri_key):
    """ 私钥签名
    :param src: 数据字符串
    :param pri_key: 私钥
    :return:
    """
    key = public_key.loads_key(base64.b64decode(pri_key))
    src = src.encode('utf-8')
    return key.sign_md5_to_base64(src)


def _sign_rsa_data(data, pri_key):
    src = _gen_sign_data(data)

    return _sign_rsa(src, pri_key)


def _verify_rsa(src, pub_key, signed):
    """ 公钥验签
    :param src: 数据字符串
    :param pub_key: 公钥
    :return:
    """
    key = public_key.loads_key(base64.b64decode(pub_key))
    return key.verify_md5_from_base64(src.encode('utf-8'), signed)


def _verify_rsa_data(data, pub_key):
    signed = data.get('sign')
    src = _gen_sign_data(data)

    return _verify_rsa(src, pub_key, signed)


def md5_sign(data, key):
    return _sign_md5_data(data, key)


def rsa_sign(data, key):
    return _sign_rsa_data(data, key)


def sign(data, sign_type):
    if sign_type == config.sign_type.MD5:
        return _sign_md5_data(data, config.MD5_key)
    elif sign_type == config.sign_type.RSA:
        return _sign_rsa_data(data, config.TRADER_PRI_KEY)
    raise Exception("unknown sign type: %s" % sign_type)


def verify(data, sign_type):
    if sign_type == config.sign_type.MD5:
        return _verify_md5_data(data, config.MD5_key)
    elif sign_type == config.sign_type.RSA:
        return _verify_rsa_data(data, config.YT_PUB_KEY)
    raise Exception("unknown sign type: %s" % sign_type)
