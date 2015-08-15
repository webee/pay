# -*- coding: utf-8 -*-
from datetime import datetime

from ..util import oid
from pytoolbox.util.enum import enum
from pytoolbox.util.dbs import db_context


_REFUND_STATE = enum(CREATED='CREATED', SUCCESS='SUCCESS', FAILED='FAILED')


@db_context
def create_refund(db, payment_id, payer_account_id, payee_account_id, amount, async_callback_url=None):
    refund_id = oid.refund_id(payer_account_id)
    fields = {
        'id': refund_id,
        'secured_payment_id': payment_id,
        'payer_account_id': payer_account_id,
        'payee_account_id': payee_account_id,
        'amount': amount,
        'state': _REFUND_STATE.CREATED,
        'created_on': datetime.now(),
        'async_callback_url': async_callback_url
    }
    db.insert('secured_refund', returns_id=True, **fields)
    return refund_id


@db_context
def find_refunded_payment_by_refund_id(db, refund_id):
    return db.get(
        """
            SELECT secured_payment.*, secured_refund.async_callback_url as refund_callback_url,
                   secured_refund.amount as refund_amount
              FROM secured_payment
                INNER JOIN secured_refund ON secured_payment.id = secured_refund.secured_payment_id
              WHERE secured_refund.id=%(refund_id)s
        """,
        refund_id=refund_id)
