# -*- coding: utf-8 -*-
from datetime import datetime

from lianlian_api.constant import SourceType, PayStep
from lianlian_api.util.bookkeeping import bookkeeping, Event
from tools.dbe import from_db, transactional, db_operate


def batch_confirm_pay_util_now():
    payments = _list_expired_payments(datetime.now())
    ids = list()
    for payment in payments:
        ids.append(_confirm_to_pay(payment))
    return ids


def confirm_payment(payment_id):
    payment = _get_expired_payment(payment_id)
    if payment:
        return _confirm_to_pay(payment)


def _list_expired_payments(timestamp):
    return from_db().list(
        """
            SELECT id, payee_account_id, amount
              FROM payment
              WHERE success = 1 AND confirm_success = 0
                AND auto_confirm_expired_on < %(expired_on)s
        """, expired_on=timestamp
    )


@db_operate
def list_expired_payment_ids(db, timestamp=None):
    timestamp = timestamp if timestamp else datetime.now()
    return db.list(
        """
            SELECT id
              FROM payment
              WHERE success = 1 AND confirm_success = 0
                AND auto_confirm_expired_on < %(expired_on)s
        """, expired_on=timestamp
    )


@db_operate
def _get_expired_payment(db, payment_id):
    return db.get(
        """
            SELECT id, payee_account_id, amount
              FROM payment
              WHERE id=%(id)s and success = 1 AND confirm_success = 0
        """, id=payment_id
    )


@transactional
def _confirm_to_pay(payment):
    payment_id = payment['id']
    account_id = payment['payee_account_id']
    amount = payment['amount']

    _update_to_be_confirmed(payment_id)
    _charge_from_frozen_account_to_business(payment_id, account_id, amount)
    _charge_from_business_account_to_cash(payment_id, account_id, amount)

    return payment_id


def _update_to_be_confirmed(payment_id):
    from_db().execute(
        """
            UPDATE payment SET confirm_success=1, confirmed_on=%(confirmed_on)s
              WHERE id=%(id)s
        """, id=payment_id, confirmed_on=datetime.now()
    )


def _charge_from_frozen_account_to_business(payment_id, account_id, amount):
    bookkeeping(Event(account_id, SourceType.PAY, PayStep.CONFIRMED, payment_id, amount),
                '-frozen', '+business')


def _charge_from_business_account_to_cash(payment_id, account_id, amount):
    bookkeeping(Event(account_id, SourceType.PAY, PayStep.SUCCESS, payment_id, amount),
                '-business', '+cash')