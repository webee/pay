# -*- coding: utf-8 -*-
# from api.constant import SourceType, PayStep
# from api.util.bookkeeping import bookkeeping, Event
from pytoolbox.util.dbe import transactional


@transactional
def confirm_payment(pay_record):
    payment_id = pay_record['id']
    account_id = pay_record['payee_account_id']
    amount = pay_record['amount']

    if transit.confirm(payment_id):
        _charge_from_frozen_account_to_business(payment_id, account_id, amount)
        _charge_from_business_account_to_cash(payment_id, account_id, amount)
        return payment_id


def _charge_from_frozen_account_to_business(payment_id, account_id, amount):
    bookkeeping(Event(account_id, SourceType.PAY, PayStep.CONFIRMED, payment_id, amount),
                '-frozen', '+business')


def _charge_from_business_account_to_cash(payment_id, account_id, amount):
    bookkeeping(Event(account_id, SourceType.PAY, PayStep.SUCCESS, payment_id, amount),
                '-business', '+cash')