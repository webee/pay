# coding=utf-8
from __future__ import unicode_literals

from api_x.config import test_pay


def generate_absolute_url(path):
    return test_pay.ROOT_URL + path


def is_sending_to_me(merchant_id):
    return merchant_id == test_pay.MERCHANT_ID


def is_success_request(data):
    return 'result' in data and data['result'] == 'SUCCESS'
