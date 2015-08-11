# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from .sign import md5_sign
from .util import datetime_to_str, now_to_str
# from . import config
from api import config


def pay(payer, ip, order_no, ordered_on, order_name, order_desc, amount, return_url, notification_url):
    req_params = {
        'version': config.LianLianPay.Pay.VERSION,
        'oid_partner': config.LianLianPay.OID_PARTNER,
        'user_id': str(payer.id),
        'sign_type': config.LianLianPay.Sign.MD5_TYPE,
        'busi_partner': config.LianLianPay.Pay.BUSIPARTNER_VIRTUAL_GOODS,
        'no_order': order_no,
        'dt_order': datetime_to_str(ordered_on),
        'name_goods': order_name,
        'info_order': order_desc,
        'money_order': str(amount),
        'notify_url': notification_url,
        'url_return': return_url,
        'userreq_ip': _encode_ip(ip),
        'valid_order': config.LianLianPay.Pay.DEFAULT_ORDER_EXPIRATION,
        'timestamp': now_to_str(),
        'risk_item': _get_risk_item(payer),
    }
    req_params = _append_md5_sign(req_params)
    return _generate_submit_form(req_params)


def _encode_ip(ip):
    return ip.replace('.', '_')


def _format_time(t):
    return t.strftime('%Y%m%d%H%M%S')


def _generate_submit_form(req_params):
    submit_page = '<form id="payBillForm" action="{0}" method="POST">'.format(config.LianLianPay.Pay.URL)
    for key in req_params:
        submit_page += '''<input type="hidden" name="{0}" value='{1}' />'''.format(key, req_params[key])
    submit_page += '<input type="submit" value="Submit" style="display:none" /></form>'
    submit_page += '<script>document.forms["payBillForm"].submit();</script>'
    return submit_page


def _append_md5_sign(req_params):
    digest = md5_sign(req_params, config.LianLianPay.Sign.MD5_KEY)
    req_params['sign'] = digest
    return req_params


def _get_risk_item(user):
    risk_item = {
        'user_info_mercht_userno': str(user.id),
        'user_info_dt_register': _format_time(user.created_on),
        'frms_ware_category': '1999'
    }
    return json.dumps(risk_item)
