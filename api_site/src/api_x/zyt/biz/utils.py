# coding=utf-8
from pytoolbox.util import strings
from pytoolbox.util import aes
from api_x.config import etc as config
from datetime import datetime

# first order time.
_start = datetime.strptime('2015-08-31 03:14:34', '%Y-%m-%d %H:%M:%S')
_SN_GEN_LEN = 26
_SN_MAX_LEN = 32


def generate_sn(user_id=0, size=_SN_GEN_LEN):
    size = size if size is not None else _SN_GEN_LEN

    d = (datetime.utcnow() - _start).total_seconds()
    s = config.Biz.TX_SN_PREFIX + str(int(d)) + '-%d-' % user_id
    l = size - len(s)
    return s + strings.gen_rand_str(l)


def generate_order_id(tx_id):
    # #->-, .->_
    d = (datetime.utcnow() - _start).total_seconds()
    s = '#' + str(tx_id) + '.' + str(int(d)) + '.'
    l = _SN_GEN_LEN - len(s)
    return s + strings.gen_rand_str(l)


def parse_order_id(order_id):
    s = order_id.split('.', 1)[0]
    return long(s[1:].split('.', 1)[0])


def is_order_id(x):
    return x.startswith('#')


def is_sn(x):
    return x.startswith('_') or x[0].isdigit()


def aes_encrypt(data, key=None):
    key = key or config.KEY
    return aes.encrypt_to_urlsafe_base64(data, key).rstrip('=')


def aes_decrypt(data, key=None):
    key = key or config.KEY
    data += str('=') * ((4 - (len(data) % 4)) % 4)
    data = str(data)
    return aes.decrypt_from_urlsafe_base64(data, key)
