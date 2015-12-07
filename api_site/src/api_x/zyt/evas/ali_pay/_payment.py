# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from api_x.config import ali_pay
from pytoolbox.util.log import get_logger
from pytoolbox.util.urls import build_url
from pytoolbox.util.sign import SignType
from .api_access import request
from . import signer

logger = get_logger(__name__)


def _get_common_params(out_trade_no, subject, body, total_fee, notify_url):
    return {
        'partner': ali_pay.PID,
        '_input_charset': ali_pay.INPUT_CHARSET,
        'payment_type': '1',  # 商品购买
        'sign_type': SignType.MD5,
        'seller_id': ali_pay.PID,
        'paymethod': ali_pay.PayMethod.DIRECT_PAY,
        'enable_paymethod': 'directPay^bankPay^creditCardExpress^debitCardExpress',
        'notify_url': notify_url,
        'out_trade_no': out_trade_no,
        'subject': subject,
        'total_fee': total_fee,
        'body': body,
    }


def pay_param(out_trade_no, subject, body, total_fee, notify_url, return_url):
    params = _get_common_params(out_trade_no, subject, body, total_fee, notify_url)
    params.update({
        'service': ali_pay.Service.DIRECT_PAY_BY_USER,
        'return_url': return_url,
        # 'qr_pay_mode': '2',
    })

    params['sign'] = signer.sign(params, params['sign_type'])
    params['_url'] = build_url(ali_pay.GATEWAY_URL, _input_charset=ali_pay.INPUT_CHARSET)
    logger.info("request ali pay WEB: {0}".format(params))

    return params


def wap_pay_param(out_trade_no, subject, body, total_fee, notify_url, return_url):
    params = _get_common_params(out_trade_no, subject, body, total_fee, notify_url)
    params.update({
        'service': ali_pay.Service.WAP_DIRECT_PAY_BY_USER,
        'return_url': return_url,
        'rn_check': 'F',
        'it_b_pay': ali_pay.PAYMENT_EXPIRE_TIME,
    })

    params['sign'] = signer.sign(params, params['sign_type'])
    params['_url'] = build_url(ali_pay.GATEWAY_URL, _input_charset=ali_pay.INPUT_CHARSET)

    logger.info("request ali pay WAP {0}".format(params))
    return params


def app_param(out_trade_no, subject, body, total_fee, notify_url):
    params = _get_common_params(out_trade_no, subject, body, total_fee, notify_url)
    params.update({
        'service': ali_pay.Service.MOBILE_SECURITYPAY_PAY,
        'rn_check': 'F',
        'it_b_pay': ali_pay.PAYMENT_EXPIRE_TIME,
    })

    order_spec = '&'.join(['%s="%s"' % (k, v) for k, v in params if v])
    sign = signer.sign_rsa(order_spec)

    order_str = "%s&sign=%s&sign_type=%s" % (order_spec, sign, SignType.RSA)
    res = {
        'order_str': order_str
    }

    logger.info("request ali pay APP {0}".format(res))
    return res


def query_trade(out_trade_no, trade_no=''):
    params = {
        'service': ali_pay.Service.SINGLE_TRADE_QUERY,
        'partner': ali_pay.PID,
        '_input_charset': ali_pay.INPUT_CHARSET,
        'sign_type': SignType.MD5,
        'out_trade_no': out_trade_no,
        'trade_no': trade_no
    }
    url = build_url(ali_pay.GATEWAY_URL, _input_charset=ali_pay.INPUT_CHARSET)

    return request(url, params)
