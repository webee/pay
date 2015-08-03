# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from datetime import datetime

from .util.oid import pay_id
from pytoolbox.util.dbe import db_context


@db_context
def new_payment(db, trade_id, payer_account_id, payee_account_id, amount):
    record_id = pay_id(payer_account_id)
    now = datetime.now()
    payment_fields = {
        'id': record_id,
        'trade_id': trade_id,
        'payer_account_id': payer_account_id,
        'payee_account_id': payee_account_id,
        'amount': amount,
        'created_on': now,
        'updated_on': now
    }
    db.insert('guaranteed_payment', **payment_fields)
    return record_id
