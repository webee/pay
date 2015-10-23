# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from api_x.config import lianlian_pay
from api_x.zyt.evas.util import datetime_to_str, now_to_str
from pytoolbox.util.sign import SignType
from . import signer


def _get_common_params(user_id, user_created_on, ip, order_no, ordered_on, order_name, order_desc, amount, notify_url):
    return {
        'oid_partner': lianlian_pay.OID_PARTNER,
        'platform': lianlian_pay.PLATFORM,
        'user_id': user_id[:32],
        'sign_type': SignType.MD5,
        'busi_partner': lianlian_pay.Payment.BusiPartner.VIRTUAL_GOODS,
        'no_order': order_no,
        'dt_order': datetime_to_str(ordered_on),
        'name_goods': order_name[:40],
        'info_order': order_desc[:255],
        'money_order': str(amount),
        'notify_url': notify_url,
        'userreq_ip': _encode_ip(ip),
        'valid_order': lianlian_pay.Payment.DEFAULT_ORDER_EXPIRATION,
        'timestamp': now_to_str(),
        'risk_item': _get_risk_item(user_id, user_created_on),
        }


def pay(user_id, user_created_on, ip, order_no, ordered_on, order_name, order_desc, amount, return_url, notify_url):
    params = {
        'version': lianlian_pay.Payment.VERSION,
        'charset_name': 'UTF-8',
        'url_return': return_url,
    }
    params.update(_get_common_params(user_id, user_created_on, ip, order_no, ordered_on,
                                     order_name, order_desc, amount, notify_url))
    params = _append_md5_sign(params)
    return _generate_submit_form(params)


def wap_pay(user_id, user_created_on, ip, order_no, ordered_on, order_name, order_desc, amount, return_url, notify_url,
            app_request=lianlian_pay.AppRequest.WAP):
    params = {
        'version': lianlian_pay.Payment.Wap.VERSION,
        'app_request': app_request,
        'url_return': return_url,
        }
    params.update(_get_common_params(user_id, user_created_on, ip, order_no, ordered_on,
                                     order_name, order_desc, amount, notify_url))

    params = _append_md5_sign(params)

    req_params = {
        'req_data': json.dumps(params)
    }
    return _generate_submit_form(req_params, lianlian_pay.Payment.Wap.URL)


def app_params(user_id, user_created_on, ip, order_no, ordered_on, order_name, order_desc, amount, notify_url):
    keys = ["busi_partner", "dt_order", "info_order", "money_order",
            "name_goods", "no_order", "notify_url", "oid_partner", "risk_item", "sign_type", "valid_order"]
    params = {}
    params.update(_get_common_params(user_id, user_created_on, ip, order_no, ordered_on,
                                     order_name, order_desc, amount, notify_url))
    return _append_md5_sign(params, keys)


def _generate_submit_form(req_params, url=lianlian_pay.Payment.URL):
    submit_page = '<meta http-equiv="content-type" content="text/html; charset=UTF-8">'
    submit_page += '<form id="payBillForm" action="{0}" method="POST">'.format(url)
    for key in req_params:
        submit_page += '''<input type="hidden" name="{0}" value='{1}' />'''.format(key, req_params[key])
    submit_page += '<input type="submit" value="Submit" style="display:none" /></form>'
    submit_page += '<script>document.forms["payBillForm"].submit();</script>'
    return submit_page


def _append_md5_sign(params, keys=None):
    sign_params = params
    if keys is not None:
        sign_params = {k: params[k] for k in keys}
    digest = signer.md5_sign(sign_params)
    params['sign'] = digest
    return params


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
