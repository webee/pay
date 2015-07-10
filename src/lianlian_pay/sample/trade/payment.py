# -*- coding: utf-8 -*-
import json
from datetime import datetime
from flask import Response

from .attr_dict import AttrDict
from .sign import sign

lianlian_config = AttrDict(
    version='1.0',
    oid_partner='201306031000001013',
    sign_type=AttrDict(
        MD5='MD5'
    ),

    MD5_key='201306031000001013',

    busi_partner=AttrDict(
        virtual_goods='101001',
        physical_goods='109001',
    ),

    default_order_expiration='10080',

    payment=AttrDict(
        url='https://yintong.com.cn/payment/bankgateway.htm',
        notify_url='www.baidu.com/notify',
        return_url='www.baidu.com/return'
    )
)


def pay(user_id, order_no, ordered_on, order_name, order_desc, amount, order_detail_url):
    req_params = {
        'version': lianlian_config.version,
        'oid_partner': lianlian_config.oid_partner,
        'user_id': user_id,
        'sign_type': lianlian_config.sign_type.MD5,
        'busi_partner': lianlian_config.busi_partner.virtual_goods,
        'no_order': order_no,
        'dt_order': _timestamp_to_string(ordered_on),
        'name_goods': order_name,
        'info_order': order_desc,
        'money_order': str(amount),
        'notify_url': lianlian_config.payment.notify_url,
        'url_return': lianlian_config.payment.return_url,
        'userreq_ip': _encode_ip('199.195.192.17'),
        'url_order': order_detail_url,
        'valid_order': lianlian_config.default_order_expiration,
        'timestamp': _get_current_timestamp(),
        'risk_item': _get_risk_item(),
    }
    req_params = _append_md5_sign(req_params)
    return Response(_generate_submit_form(req_params), status=200, mimetype='text/html')


def _encode_ip(ip):
    return ip.replace('.', '_')


def _generate_submit_form(req_params):
    submit_page = '<form id="payBillForm" action="{0}" method="POST">'.format(lianlian_config.payment.url)
    for key in req_params:
        submit_page += '<input type="hidden" name="{0}" value="{1}" />'.format(key, req_params[key])
    submit_page += '<input type="submit" value="Submit" style="display:none" /></form>'
    submit_page += '<script>document.forms["payBillForm"].submit();</script>'
    return submit_page


def _timestamp_to_string(timestamp):
    return timestamp.strftime('%Y%m%d%H%M%S')


def _get_current_timestamp():
    return _timestamp_to_string(datetime.now())


def _get_risk_item():
    risk_item = {
        'user_info_full_name': 'Hello',
        'frms_ware_category': '1999'
    }
    return json.dumps(risk_item)


def _append_md5_sign(req_params):
    digest = sign(req_params, lianlian_config.sign_type.MD5, lianlian_config.MD5_key)
    req_params['sign'] = digest
    return req_params
