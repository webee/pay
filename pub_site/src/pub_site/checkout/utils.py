# coding=utf-8
from __future__ import unicode_literals
from pytoolbox.util import times, aes
from pub_site import config


def gen_payment_token(sn):
    timestamp = times.timestamp()
    expired = timestamp + config.Checkout.PAYMENT_CHECKOUT_VALID_SECONDS

    key = _gen_key(sn)
    data = str(int(expired))

    return str(aes.encrypt_to_urlsafe_base64(data, key).rstrip('='))


def check_payment_token(sn, token):
    try:
        token += '=' * ((4 - (len(token) % 4)) % 4)
        key = _gen_key(sn)
        expired = int(aes.decrypt_from_urlsafe_base64(str(token), str(key)))
    except:
        return False

    timestamp = times.timestamp()
    return timestamp < expired


def _gen_key(sn):
    return sn[:8] + config.Checkout.AES_KEY
