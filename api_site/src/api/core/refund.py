# -*- coding: utf-8 -*-
from datetime import datetime

from ._dba import find_payment_by_trade_id, create_refund, update_refund_result, find_refund_by_id, REFUND_STATE, \
    transit_refund_state
from .ipay import transaction
from .util.handling_result import HandledResult
from ._bookkeeping import bookkeep, Event, SourceType
from pytoolbox.util.dbe import transactional
from pytoolbox.util.log import get_logger

_logger = get_logger(__name__)


def refund(payment_trade_id, amount, trade_info):
    pay_record = find_payment_by_trade_id(payment_trade_id)

    payer_account_id = pay_record['payee_account_id']
    payee_account_id = pay_record['payer_account_id']
    paybill_id = pay_record['paybill_id']
    now = datetime.now()
    refund_id = create_refund(pay_record['id'], payer_account_id, payee_account_id, amount, trade_info, now)

    _request_refund(refund_id, now, amount, paybill_id)


def get_refund_by_id(refund_id):
    return find_refund_by_id(refund_id)


@transactional
def handle_refund_notification(refund_record, refund_serial_no, status):
    refund_id = refund_record['id']
    update_refund_result(refund_id, refund_serial_no)
    _logger.warn(
        "Refund notify result: id={0}, refund_serial_no={1}, status={2}".format(refund_id, refund_serial_no, status))

    # process refund status.
    if transaction.is_successful_refund(status):
        transit_refund_state(refund_id, REFUND_STATE.CREATED, REFUND_STATE.SUCCESS)
        _bookkeep(refund_record)
        return HandledResult(True, True)
    else:
        transit_refund_state(refund_id, REFUND_STATE.CREATED, REFUND_STATE.FAILED)
        return HandledResult(True, False)


def _request_refund(refund_id, refunded_on, amount, paybill_id):
    resp = transaction.refund(refund_id, refunded_on, amount, paybill_id)
    if 'oid_refundno' in resp:
        refund_serial_no = resp['oid_refundno']
        update_refund_result(refund_id, refund_serial_no)


def _bookkeep(refund_record):
    pay_record = find_refund_by_id(refund_record['payment_id'])
    payer_account_id = pay_record['payer_account_id']
    bookkeep(Event(SourceType.REFUND, refund_record['id'], refund_record['amount']),
             (payer_account_id, '-cash'),
             (payer_account_id, '-asset'))
