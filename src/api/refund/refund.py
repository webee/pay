# -*- coding: utf-8 -*-
from datetime import datetime
from urlparse import urljoin

from api.util import timestamp
import requests
from . import config
from api.account.account import find_account_id
from api.util.sign import md5_sign
from api.util.uuid import encode_uuid
from tools.dbi import from_db, transactional


class NoTransactionFoundException(Exception):
    def __init__(self, client_id, order_no):
        message = "Cannot find any valid pay transaction with [client_id={0}, order_no={1}]."\
            .format(client_id, order_no)
        super(NoTransactionFoundException, self).__init__(message)


class RefundFailedException(Exception):
    def __init__(self, refund_id):
        message = "Refund application has been created, but actual refunding is failed [refund_id={0}]."\
            .format(refund_id)
        super(RefundFailedException, self).__init__(message)
        self.refund_id = refund_id


def refund_transaction(client_id, payer_id, order_no, amount, url_root):
    transaction = _find_payment(client_id, order_no)
    if not transaction:
        raise NoTransactionFoundException(client_id, order_no)

    payer_account_id = find_account_id(client_id, payer_id)
    refund_id, refunded_on = _apply_for_refund(transaction['id'], payer_account_id, amount)

    _apply_to_refund(refund_id, refunded_on, amount, transaction['paybill_id'],
                     _generate_notification_url(url_root, config.refund.notify_url, _encode_uuid(refund_id)))


def _apply_to_refund(refund_id, refunded_on, amount, paybill_id, notification_url):
    req_params = {
        'oid_partner': config.oid_partner,
        'sign_type': config.sign_type.MD5,
        'no_refund': str(refund_id),
        'dt_refund': timestamp.to_str(refunded_on),
        'money_refund': str(amount),
        'oid_paybill': paybill_id,
        'notify_url': notification_url
    }
    req_params = _append_md5_sign(req_params)
    resp = requests.post(config.refund.url, req_params)

    if resp.status_code != 200:
        raise RefundFailedException(refund_id)
    return_values = resp.json()
    if return_values['ret_code'] != '0000':
        raise RefundFailedException(refund_id)


def _find_payment(client_id, order_no):
    return from_db().get(
        """
            SELECT id, paybill_id
              FROM payment
              WHERE client_id = %(client_id)s AND order_id = %(order_id)s AND success = 1
        """,
        client_id=client_id, order_id=order_no)


@transactional
def _apply_for_refund(transaction_id, payer_account_id, amount):
    refunded_on = datetime.now()
    fields = {
        'transaction_id': transaction_id,
        'payer_account_id': payer_account_id,
        'amount': amount,
        'created_on': refunded_on
    }
    refund_id = from_db().insert('refund', **fields)
    return refund_id, refunded_on


def _encode_uuid(refund_id):
    return encode_uuid('%0.8d' % refund_id)


def _generate_transaction_id(payer_account_id):
    return datetime.now().strftime("%Y%m%d%H%M%S%f") + '%0.7d' % payer_account_id


def _generate_notification_url(url_root, relative_url, uuid):
    params = {'uuid': uuid}
    relative_url = relative_url.format(**params)
    return urljoin(url_root, relative_url)


def _append_md5_sign(req_params):
    digest = md5_sign(req_params, config.MD5_key)
    req_params['sign'] = digest
    return req_params