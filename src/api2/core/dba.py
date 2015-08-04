# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from datetime import datetime

from .util.oid import pay_id
from api2.util.enum import enum
from pytoolbox.util.dbe import db_context


_BANK_ACCOUNT = enum(IsPrivateAccount=0, IsCorporateAccount=1)


@db_context
def new_payment(db, trade_id, payer_account_id, payee_account_id, amount):
    record_id = pay_id(payer_account_id)
    now = datetime.now()
    fields = {
        'id': record_id,
        'trade_id': trade_id,
        'payer_account_id': payer_account_id,
        'payee_account_id': payee_account_id,
        'amount': amount,
        'created_on': now,
        'updated_on': now
    }
    db.insert('payment', **fields)
    return record_id


@db_context
def find_payment_by_id(db, id):
    return db.get('SELECT * FROM payment WHERE id = %(id)s', id=id)


@db_context
def succeed_payment(db, id, paybill_id):
    now = datetime.now()
    db.execute(
        """
            UPDATE payment
              SET state = 'SUCCESS', transaction_ended_on = %(ended_on)s, paybill_id = %(paybill_id)s
              WHERE id = %(id)s
        """,
        id=id, paybill_id=paybill_id, ended_on=now)


@db_context
def fail_payment(db, id):
    db.execute("UPDATE payment SET state = 'FAILED', transaction_ended_on = %(ended_on)s WHERE id = %(id)s",
               id=id, ended_on=datetime.now())


@db_context
def new_transfer(db, trade_id, payer_account_id, payee_account_id, amount):
    fields = {
        'trade_id': trade_id,
        'payer_account_id': payer_account_id,
        'payee_account_id': payee_account_id,
        'amount': amount,
        'created_on': datetime.now()
    }
    db.insert('guaranteed_payment', **fields)


@db_context
def query_all_bankcards(db, account_id):
    return db.list("SELECT * FROM bankcard WHERE account_id=%(account_id)s", account_id=account_id)


@db_context
def new_bankcard(db, account_id, bankcard):
    fields = {
        'account_id': account_id,
        'card_no': bankcard.no,
        'card_type': bankcard.card_type,
        'account_name': bankcard.account_name,
        'flag': _BANK_ACCOUNT.IsCorporateAccount if bankcard.is_corporate_account else _BANK_ACCOUNT.IsPrivateAccount,
        'bank_code': bankcard.bank_code,
        'province_code': bankcard.province_code,
        'city_code': bankcard.city_code,
        'bank_name': bankcard.bank_name,
        'branch_bank_name': bankcard.branch_bank_name,
        'created_on': datetime.now()
    }
    return db.insert('bankcard', returns_id=True, **fields)