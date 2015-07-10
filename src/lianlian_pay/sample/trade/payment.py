# -*- coding: utf-8 -*-
import json
from datetime import datetime
from flask import Response

from . import lianlian_base_config
from .attr_dict import AttrDict
from .sign import sign

lianlian_payment_config = AttrDict(
    sign_type=AttrDict(
        MD5='MD5'
    ),

    MD5_key='201408071000001546_test_20140815',

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
config = lianlian_payment_config.merge_to(lianlian_base_config)


def pay(user_id, order_no, ordered_on, order_name, order_desc, amount):
    req_params = {
        'version': config.version,
        'oid_partner': config.oid_partner,
        'user_id': user_id,
        'sign_type': config.sign_type.MD5,
        'busi_partner': config.busi_partner.virtual_goods,
        'no_order': order_no,
        'dt_order': _timestamp_to_string(ordered_on),
        'name_goods': order_name,
        'info_order': order_desc,
        'money_order': str(amount),
        'notify_url': config.payment.notify_url,
        'url_return': config.payment.return_url,
        'userreq_ip': _encode_ip('199.195.192.17'),
        'valid_order': config.default_order_expiration,
        'timestamp': _get_current_timestamp(),
        # 'risk_item': _get_risk_item(),
    }
    req_params = _append_md5_sign(req_params)
    return Response(_generate_submit_form(req_params), status=200, mimetype='text/html')


def _encode_ip(ip):
    return ip.replace('.', '_')


def _generate_submit_form(req_params):
    submit_page = '<form id="payBillForm" action="{0}" method="POST">'.format(config.payment.url)
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
    digest = sign(req_params, config.sign_type.MD5, config.MD5_key)
    req_params['sign'] = digest
    return req_params
