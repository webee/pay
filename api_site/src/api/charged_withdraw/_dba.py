# -*- coding: utf-8 -*-
from datetime import datetime

from .util.oid import charged_withdraw_id
from pytoolbox.util.enum import enum
from pytoolbox.util.dbe import db_context


CHARGED_WITHDRAW_STATE = enum(CREATED='CREATED', CHARGED_FEE='CHARGED_FEE', SUCCESS='SUCCESS',
                               REFUNDED_FEE='REFUNDED_FEE')


@db_context
def create_charged_withdraw(db, account_id, bankcard_id, actual_withdraw_amount, charged_fee, callback_url):
    record_id = charged_withdraw_id(account_id)
    now = datetime.now()
    fields = {
        'id': record_id,
        'account_id': account_id,
        'bankcard_id': bankcard_id,
        'actual_withdraw_amount': actual_withdraw_amount,
        'fee': charged_fee,
        'async_callback_url': callback_url,
        'state': CHARGED_WITHDRAW_STATE.CREATED,
        'created_on': now,
        'updated_on': now
    }
    db.insert('charged_withdraw', **fields)
    return record_id


@db_context
def update_withdraw_state(db, _id, state):
    db.execute(
        """
            UPDATE charged_withdraw SET state=%(new_state)s
              WHERE id = %(id)s
        """,
        id=_id, new_state=state)