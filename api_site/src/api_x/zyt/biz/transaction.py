# coding=utf-8
from __future__ import unicode_literals

from api_x.constant import TransactionState
from api_x.dbs import transactional
from api_x import db
from .models import TransactionRecord, TransactionStateLog, UserTransaction
from .utils import generate_sn


class TransactionError(Exception):
    def __init__(self, msg):
        super(TransactionError, self).__init__(msg)


class TransactionNotFoundError(TransactionError):
    def __init__(self, tx_id):
        msg = "transaction: [id: {0}] state error.".format(tx_id)
        super(TransactionNotFoundError, self).__init__(msg)


class TransactionStateError(TransactionError):
    def __init__(self, tx_id):
        msg = "transaction: [id: {0}] state error.".format(tx_id)
        super(TransactionStateError, self).__init__(msg)


@transactional
def create_transaction(tp, amount, comments, user_ids):
    sn = generate_sn(user_ids[0])
    record = TransactionRecord(sn=sn, amount=amount, state=TransactionState.CREATED, type=tp, comments=comments)
    for user_id in user_ids:
        user_transaction = UserTransaction(user_id=user_id, tx_record=record)
        db.session.add(user_transaction)

    db.session.add(record)

    return record


def get_tx_by_id(transaction_id):
    return TransactionRecord.query.get(transaction_id)


def get_tx_by_sn(transaction_sn):
    return TransactionRecord.query.filter_by(sn=transaction_sn).first()


@transactional
def transit_transaction_state(tx_id, cur_state, new_state, event_id=None):
    tx = TransactionRecord.query.get(tx_id)
    if tx is None:
        raise TransactionNotFoundError(tx_id)

    if tx.state != cur_state:
        raise TransactionStateError(tx_id)

    tx.state = new_state
    db.session.add(tx)

    _log_state_transit(tx.id, cur_state, new_state, event_id)


def _log_state_transit(tx_id, prev_state, state, event_id=None):
    if event_id is None:
        tx_state_log = TransactionStateLog(tx_id=tx_id, prev_state=prev_state, state=state)
        db.session.add(tx_state_log)
    else:
        event_ids = [event_id]
        if isinstance(event_id, list):
            event_ids = event_id

        for event_id in event_ids:
            tx_state_log = TransactionStateLog(tx_id=tx_id, prev_state=prev_state, state=state, event_id=event_id)
            db.session.add(tx_state_log)


@transactional
def update_transaction_info(tx_id, vas_name, vas_sn, state=None):
    tx = TransactionRecord.query.get(tx_id)
    if tx is None:
        raise TransactionNotFoundError(tx_id)

    tx.vas_name = vas_name
    tx.vas_sn = vas_sn
    if state is not None:
        tx.state = state

    db.session.add(tx)

    return tx