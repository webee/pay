# -*- coding: utf-8 -*-
from ._bookkeeping import bookkeep, Event, SourceType
from ._dba import find_payment_by_id, succeed_payment as _succeed_payment, fail_payment as _fail_payment
from api.util.uuid import decode_uuid
from pytoolbox.util.dbe import transactional


def is_valid_payment(payment_id, uuid, paid_amount):
    if payment_id != decode_uuid(uuid):
        return False

    pay_record = find_payment_by_id(payment_id)
    return pay_record['amount'] == paid_amount


def is_successful_payment(pay_result):
    return pay_result.upper() == 'SUCCESS'


@transactional
def fail_payment(payment_id):
    _fail_payment(payment_id)


@transactional
def succeed_payment(payment_id, paybill_id):
    _succeed_payment(payment_id, paybill_id)
    pay_record = find_payment_by_id(payment_id)
    _bookkeep(pay_record)

    return pay_record


def find_payment_by_uuid(uuid):
    payment_id = decode_uuid(uuid)
    return find_payment_by_id(payment_id)


def _bookkeep(pay_record):
    payee_account_id = pay_record['payee_account_id']
    bookkeep(Event(SourceType.PAY, pay_record['id'], pay_record['amount']),
             (payee_account_id, '+asset'),
             (payee_account_id, '+cash'))
