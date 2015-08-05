# -*- coding: utf-8 -*-
from datetime import datetime

from ..util import oid
from api2.util.enum import enum
from pytoolbox.util.dbe import db_context


_REFUND_STATE = enum(CREATED='CREATED', SUCCESS='SUCCESS', FAILED='FAILED')


@db_context
def create_refund(db, payment_id, payer_account_id, payee_account_id, amount, async_callback_url=None):
    refund_id = oid.refund_id(payer_account_id)
    fields = {
        'id': refund_id,
        'payment_id': payment_id,
        'payer_account_id': payer_account_id,
        'payee_account_id': payee_account_id,
        'amount': amount,
        'state': _REFUND_STATE.CREATED,
        'created_on': datetime.now(),
        'async_callback_url': async_callback_url
    }
    db.insert('refund', returns_id=True, **fields)
    return refund_id
