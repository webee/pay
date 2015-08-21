# coding=utf-8
from __future__ import unicode_literals

from api_x.constant import TransactionState
from pytoolbox.util.dbs import transactional
from api_x import db
from ..models import Transaction, TransactionStateLog
from ..models import UserTransaction
from ..utils import generate_sn
from .error import TransactionError, TransactionNotFoundError, TransactionStateError


@transactional
def create_transaction(tp, amount, comments, user_id_roles):
    sn = generate_sn(user_id_roles[0][0])
    tx = Transaction(sn=sn, amount=amount, state=TransactionState.CREATED, type=tp, comments=comments)
    for user_id, role in user_id_roles:
        user_transaction = UserTransaction(user_id=user_id, tx=tx, role=role)
        db.session.add(user_transaction)

    db.session.add(tx)

    return tx


@transactional
def transit_transaction_state(tx_id, cur_state, new_state, event_id=None):
    tx = Transaction.query.get(tx_id)
    if tx is None:
        raise TransactionNotFoundError(tx_id)

    if tx.state != cur_state:
        raise TransactionStateError()

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
    tx = Transaction.query.get(tx_id)
    if tx is None:
        raise TransactionNotFoundError(tx_id)

    tx.vas_name = vas_name
    tx.vas_sn = vas_sn
    if state is not None:
        tx.state = state

    db.session.add(tx)

    return tx


def query_user_transactions(account_user_id, role, page, per_page, q):
    from sqlalchemy.orm import lazyload

    query = UserTransaction.query.options(lazyload('tx')). \
        outerjoin(Transaction). \
        filter(UserTransaction.user_id == account_user_id)
    if role:
        query = query.filter(UserTransaction.role == role)
    if q:
        query = query.filter(Transaction.comments.contains(q))
    query = query.order_by(Transaction.created_on.desc())
    paginator = query.paginate(page, per_page, error_out=False)

    return paginator.total, paginator.items