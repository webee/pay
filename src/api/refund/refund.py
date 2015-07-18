# -*- coding: utf-8 -*-
from datetime import datetime

from api.constant import SourceType, RefundStep
from api.util import id
from api.util.bookkeeping import bookkeeping, Event
from api.util.enum import enum
from api.util.ipay import transaction
from api.util.uuid import decode_uuid
from api.account.account import find_account_id
from tools.dbi import from_db, transactional


RefundState = enum(Applied=0, InProcessing=1, Success=2, Failure=3)


class NoPaymentFoundError(Exception):
    def __init__(self, client_id, order_no):
        message = "Cannot find any valid pay transaction with [client_id={0}, order_no={1}]."\
            .format(client_id, order_no)
        super(NoPaymentFoundError, self).__init__(message)


class RefundFailedError(Exception):
    def __init__(self, refund_id):
        message = "Refund application has been created, but actual refunding is failed [refund_id={0}]."\
            .format(refund_id)
        super(RefundFailedError, self).__init__(message)
        self.refund_id = refund_id


def refund_transaction(client_id, payer_id, order_no, amount, url_root):
    payment = _find_payment(client_id, order_no)
    if not payment:
        raise NoPaymentFoundError(client_id, order_no)

    payer_account_id = find_account_id(client_id, payer_id)
    refund_id, refunded_on = _refund(payment['id'], payer_account_id, amount)
    _send_refund_request(refund_id, refunded_on, amount, payment['paybill_id'], url_root)


def is_valid_refund(refund_id, uuid, refund_amount):
    if refund_id != decode_uuid(uuid):
        return False

    amount = from_db().get_scalar('SELECT amount FROM refund WHERE id = %(id)s AND success IS NULL',
                                  id=refund_id)
    return amount == refund_amount


def is_successful_refund(result):
    return int(result) == RefundState.Success


def _send_refund_request(refund_id, refunded_on, amount, paybill_id, url_root):
    resp = transaction.refund(refund_id, refunded_on, amount, paybill_id)

    if resp.status_code != 200:
        raise RefundFailedError(refund_id)
    return_values = resp.json()
    if return_values['ret_code'] != '0000':
        raise RefundFailedError(refund_id)


def _find_payment(client_id, order_no):
    return from_db().get(
        """
            SELECT id, paybill_id
              FROM payment
              WHERE client_id = %(client_id)s AND order_id = %(order_id)s AND success = 1
        """,
        client_id=client_id, order_id=order_no)


@transactional
def _refund(payment_id, payer_account_id, amount):
    refund_id, refunded_on = _apply_for_refund(payment_id, payer_account_id, amount)
    bookkeeping(
        Event(payer_account_id, SourceType.REFUND, RefundStep.FROZEN, refund_id, amount),
        '-secured', '+frozen'
    )
    return refund_id, refunded_on


def _apply_for_refund(payment_id, payer_account_id, amount):
    refunded_on = datetime.now()
    fields = {
        'id': id.refund_id(payer_account_id),
        'payment_id': payment_id,
        'payer_account_id': payer_account_id,
        'amount': amount,
        'created_on': refunded_on
    }
    refund_id = from_db().insert('refund', returns_id=True, **fields)
    return refund_id, refunded_on

