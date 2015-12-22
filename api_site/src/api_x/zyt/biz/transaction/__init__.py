# coding=utf-8
from __future__ import unicode_literals

from api_x.constant import TransactionState
from pytoolbox.util.dbs import transactional
from api_x import db
from . import dba
from ..models import Transaction, TransactionStateLog
from ..models import UserTransaction
from ..utils import generate_sn
from .error import TransactionError, TransactionNotFoundError, TransactionStateError


@transactional
def create_transaction(channel_name, tp, amount, comments, role_users, vas_name=None,
                       order_id=None,
                       state=None, super_id=None, use_date_sn=False):
    if state is None:
        state = TransactionState.CREATED

    # [(user_id, role), ...]
    user_id = role_users[0].user_id
    sn = generate_sn(user_id, use_date_sn)
    while dba.get_tx_by_sn(sn) is not None:
        sn = generate_sn(user_id)
    tx = Transaction(sn=sn, channel_name=channel_name, order_id=order_id,
                     amount=amount, state=state, type=tp, comments=comments, super_id=super_id)
    if vas_name is not None:
        tx.vas_name = vas_name
    for role_user in role_users:
        user_transaction = UserTransaction(user_id=role_user.user_id, tx=tx, role=role_user.role)
        db.session.add(user_transaction)

    db.session.add(tx)

    return tx


@transactional
def add_tx_user(tx_id, role_user):
    user_transaction = UserTransaction(user_id=role_user.user_id, tx_id=tx_id, role=role_user.role)
    db.session.add(user_transaction)


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
    tx_state_logs = []
    if event_id is None:
        tx_state_log = TransactionStateLog(tx_id=tx_id, prev_state=prev_state, state=state)
        tx_state_logs.append(tx_state_log)
    else:
        event_ids = [event_id]
        if isinstance(event_id, list):
            event_ids = event_id

        for event_id in event_ids:
            tx_state_log = TransactionStateLog(tx_id=tx_id, prev_state=prev_state, state=state, event_id=event_id)
            tx_state_logs.append(tx_state_log)
    group_id = None
    for tx_state_log in tx_state_logs:
        db.session.add(tx_state_log)
        if group_id is None:
            db.session.flush()
            group_id = tx_state_log.id
        tx_state_log.group_id = group_id
        db.session.add(tx_state_log)


@transactional
def update_transaction_info(tx_id, vas_sn, vas_name=None, state=None):
    tx = Transaction.query.get(tx_id)
    if tx is None:
        raise TransactionNotFoundError(tx_id)

    tx.vas_sn = vas_sn
    if vas_name is not None:
        tx.vas_name = vas_name
    if state is not None:
        tx.state = state

    db.session.add(tx)

    return tx


def query_user_transactions(account_user_id, role, page, per_page, q, vas_name):
    from sqlalchemy.orm import lazyload
    from sqlalchemy import or_

    query = UserTransaction.query.options(lazyload('tx')). \
        outerjoin(Transaction). \
        filter(UserTransaction.user_id == account_user_id)
    if role:
        query = query.filter(UserTransaction.role == role)
    if vas_name:
        query = query.filter(Transaction.vas_name == vas_name)
    if q:
        query = query.filter(or_(Transaction.comments.contains(q),
                                 Transaction.order_id.contains(q),
                                 Transaction.state == q.upper()))
    query = query.order_by(Transaction.created_on.desc())
    paginator = query.paginate(page, per_page, error_out=False)

    return paginator.total, paginator.items
