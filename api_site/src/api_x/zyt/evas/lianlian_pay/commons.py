# coding=utf-8
from __future__ import unicode_literals

from api_x.config import lianlian_pay


def generate_absolute_url(path):
    return lianlian_pay.ROOT_URL + path


def is_sending_to_me(partner_id):
    return partner_id == lianlian_pay.OID_PARTNER


def is_success_request(data):
    return 'ret_code' in data or data['ret_code'] == '0000'
