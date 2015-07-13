# -*- coding: utf-8 -*-
import json
from datetime import datetime

from . import config
from .sign import sign
from .uuid import decode_uuid
from tools.dbi import from_db


def pay_by_uuid(transaction_uuid):
    transaction_id = decode_uuid(transaction_uuid)
    transaction = from_db().get(
        """
            SELECT payer_account_id, order_id, product_name, product_desc, amount, ordered_on, callback_url
              FROM payment
              WHERE id = %(id)s
        """,
        id=transaction_id)
    return _pay(payer_account_id=transaction['payer_account_id'],
                order_no=transaction_id,
                order_name=transaction['product_name'],
                order_desc=transaction['product_desc'],
                ordered_on=transaction['ordered_on'],
                amount=transaction['amount'],
                notification_url=transaction['callback_url'])


def _pay(payer_account_id, order_no, ordered_on, order_name, order_desc, amount, notification_url):
    req_params = {
        'version': config.version,
        'oid_partner': config.oid_partner,
        'user_id': str(payer_account_id),
        'sign_type': config.sign_type.MD5,
        'busi_partner': config.busi_partner.virtual_goods,
        'no_order': order_no,
        'dt_order': _timestamp_to_string(ordered_on),
        'name_goods': order_name,
        'info_order': order_desc,
        'money_order': str(amount),
        'notify_url': notification_url,
        'url_return': config.payment.return_url,
        'userreq_ip': _encode_ip('199.195.192.17'),
        'valid_order': config.default_order_expiration,
        'timestamp': _stringify_current_timestamp(),
        # 'risk_item': _get_risk_item(),
    }
    req_params = _append_md5_sign(req_params)
    return _generate_submit_form(req_params)


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


def _stringify_current_timestamp():
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
