# -*- coding: utf-8 -*-

from . import payment
from api.constant import SourceType, PayStep
import api.payment.transit
from api.util.bookkeeping import bookkeeping, Event
from tools.dbe import transactional


def list_all_expired_payments():
    return payment.list_expired()


@transactional
def confirm_payment(payment_id):
    pay_record = payment.find(payment_id)
    payment_id = pay_record['id']
    account_id = pay_record['payee_account_id']
    amount = pay_record['amount']

    if api.payment.transit.confirm(payment_id):
        _charge_from_frozen_account_to_business(payment_id, account_id, amount)
        _charge_from_business_account_to_cash(payment_id, account_id, amount)
        return payment_id


def _charge_from_frozen_account_to_business(payment_id, account_id, amount):
    bookkeeping(Event(account_id, SourceType.PAY, PayStep.CONFIRMED, payment_id, amount),
                '-frozen', '+business')


def _charge_from_business_account_to_cash(payment_id, account_id, amount):
    bookkeeping(Event(account_id, SourceType.PAY, PayStep.SUCCESS, payment_id, amount),
                '-business', '+cash')