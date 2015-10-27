# coding=utf-8
from __future__ import unicode_literals

from api_x.config import lianlian_pay
from api_x.zyt.evas.error import ApiError


def generate_absolute_url(path):
    return lianlian_pay.ROOT_URL + path


def is_sending_to_me(partner_id):
    return partner_id == lianlian_pay.OID_PARTNER


def get_pure_result(res):
    return {k: v for k, v in res.items() if k not in {'ret_code', 'ret_msg', 'sign_type', 'sign'}}
