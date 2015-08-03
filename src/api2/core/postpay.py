# -*- coding: utf-8 -*-
from .bookkeeping import bookkeep, Event, SourceType
from .dba import find_payment_by_id, succeed_payment as _succeed_payment, fail_payment as _fail_payment
from api2.util.uuid import decode_uuid
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
    bookkeep(Event(SourceType.PAY, payment_id, pay_record['amount']),
             pay_record['payer_account_id'], pay_record['payee_account_id'])


def find_payment_by_uuid(uuid):
    payment_id = decode_uuid(uuid)
    return find_payment_by_id(payment_id)
