# coding=utf-8
from __future__ import unicode_literals
from pytoolbox.util.sign import SignType
from datetime import datetime
from api_x.config import ali_pay as config
from pytoolbox.util.urls import build_url
from .api_access import request


def do_refund(batch_no, trade_no, refund_fee, notify_url, dback_notify_url, info=None):
    info = info if info else "程序退款"
    detail_data = '%s^%s^%s' % (trade_no, refund_fee, info)
    params = {
        'service': config.Service.REFUND_NOPWD_URL,
        'partner': config.PID,
        '_input_charset': config.INPUT_CHARSET,
        'sign_type': SignType.MD5,
        'notify_url': notify_url,
        'dback_notify_url': dback_notify_url,
        'batch_no': batch_no,
        'refund_date': _current_date_time(),
        'batch_num': '1',
        'detail_data': detail_data,
    }

    url = build_url(config.GATEWAY_URL, _input_charset=config.INPUT_CHARSET)

    return request(url, params)


def query_refund(out_trade_no, trade_no=''):
    from ._payment import query_trade
    pass


def _current_date_time():
    dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')
