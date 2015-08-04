# -*- coding: utf-8 -*-
from datetime import datetime

from .dba import find_payment_by_trade_id, create_refund, update_refund_result
from .ipay import transaction


def refund(payment_trade_id, amount):
    pay_record = find_payment_by_trade_id(payment_trade_id)

    payer_account_id = pay_record['payee_account_id']
    payee_account_id = pay_record['payer_account_id']
    paybill_id = pay_record['paybill_id']
    now = datetime.now()
    refund_id = create_refund(pay_record['id'], payer_account_id, payee_account_id, amount, now)

    _request_refund(refund_id, now, amount, paybill_id)


def _request_refund(refund_id, refunded_on, amount, paybill_id):
    resp = transaction.refund(refund_id, refunded_on, amount, paybill_id)
    if 'oid_refundno' in resp:
        refund_serial_no = resp['oid_refundno']
        update_refund_result(refund_id, refund_serial_no)
