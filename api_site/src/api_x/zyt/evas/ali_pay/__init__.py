# coding=utf-8
from __future__ import unicode_literals
from flask import url_for
from .commons import generate_absolute_url
from pytoolbox.util.sign import Signer
from pytoolbox.util.log import get_logger
from ..error import PaymentTypeNotSupportedError
from api_x.config import ali_pay as config


logger = get_logger(__name__)

NAME = 'ALI_PAY'

signer = Signer(md5_key_param_name=None, sign_key_name='sign', ignore_keys={'sign_type'}, include_keys={'_input_charset'})


def payment_param(payment_type, source, out_trade_no, subject, body, total_fee):
    from ._payment import pay_param as _pay_param, wap_pay_param as _wap_pay_param, app_param as _app_param

    notify_url = generate_absolute_url(url_for('ali_pay_entry.pay_notify', source=source))
    return_url = generate_absolute_url(url_for('ali_pay_entry.pay_result'))

    subject = subject[:128]
    body = body[:512]
    total_fee = str(total_fee)

    if payment_type == config.PaymentType.WEB:
        return _pay_param(out_trade_no, subject, body, total_fee, notify_url, return_url)
    elif payment_type == config.PaymentType.WAP:
        return _wap_pay_param(out_trade_no, subject, body, total_fee, notify_url, return_url)
    elif payment_type == config.PaymentType.APP:
        return _app_param(out_trade_no, subject, body, total_fee, notify_url)
    else:
        raise PaymentTypeNotSupportedError(NAME, payment_type)
