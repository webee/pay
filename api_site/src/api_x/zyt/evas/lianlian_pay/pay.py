# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from api_x.config import lianlian_pay
from .sign import md5_sign
from .util import datetime_to_str, now_to_str


def pay(user_id, user_created_on, ip, order_no, ordered_on, order_name, order_desc, amount, return_url, notify_url):
    req_params = {
        'version': lianlian_pay.Payment.VERSION,
        'oid_partner': lianlian_pay.OID_PARTNER,
        'user_id': str(user_id),
        'sign_type': lianlian_pay.SignType.MD5,
        'busi_partner': lianlian_pay.Payment.BusiPartner.VIRTUAL_GOODS,
        'no_order': order_no,
        'dt_order': datetime_to_str(ordered_on),
        'name_goods': order_name[:50],
        'info_order': order_desc[:50],
        'money_order': str(amount),
        'notify_url': notify_url,
        'url_return': return_url,
        'userreq_ip': _encode_ip(ip),
        'valid_order': lianlian_pay.Payment.DEFAULT_ORDER_EXPIRATION,
        'timestamp': now_to_str(),
        'risk_item': _get_risk_item(user_id, user_created_on),
    }
    req_params = _append_md5_sign(req_params)
    return _generate_submit_form(req_params)


def _generate_submit_form(req_params):
    submit_page = '<form id="payBillForm" action="{0}" method="POST">'.format(lianlian_pay.Payment.URL)
    for key in req_params:
        submit_page += '''<input type="hidden" name="{0}" value='{1}' />'''.format(key, req_params[key])
    submit_page += '<input type="submit" value="Submit" style="display:none" /></form>'
    submit_page += '<script>document.forms["payBillForm"].submit();</script>'
    return submit_page


def _append_md5_sign(req_params):
    digest = md5_sign(req_params, lianlian_pay.MD5_KEY)
    req_params['sign'] = digest
    return req_params


def _get_risk_item(user_id, user_created_on):
    risk_item = {
        'user_info_mercht_userno': str(user_id),
        'user_info_dt_register': _format_time(user_created_on),
        'frms_ware_category': '1999'
    }
    return json.dumps(risk_item)


def _format_time(t):
    return t.strftime('%Y%m%d%H%M%S')


def _encode_ip(ip):
    return ip.replace('.', '_')
