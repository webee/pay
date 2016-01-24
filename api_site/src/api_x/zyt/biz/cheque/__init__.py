# coding=utf-8
from __future__ import unicode_literals

from api_x import db
from api_x.constant import ChequeTxState
from api_x.zyt.biz.transaction import add_tx_user
from api_x.zyt.biz.transaction.dba import get_tx_by_id, get_tx_by_sn
from api_x.zyt.vas.pattern import zyt_bookkeeping, transfer_frozen, transfer
from api_x.zyt.vas.models import EventType
from api_x.zyt.biz.transaction import create_transaction, transit_transaction_state, update_transaction_info
from api_x.zyt.biz.models import TransactionType, ChequeType, ChequeRecord
from api_x.zyt.biz.error import NonPositiveAmountError, AmountValueError
from api_x.zyt.biz import user_roles
from api_x.zyt.user_mapping import get_user_map_by_account_user_id
from pytoolbox.util.dbs import transactional, require_transaction_context
from pytoolbox.util.log import get_logger
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta
from api_x.task import tasks
from .error import BadCashChequeTokenError, CashChequeError
from .utils import gen_signature


logger = get_logger(__name__)


@transactional
def draw_cheque(channel, from_id, amount, order_id=None, valid_seconds=1800, cheque_type=ChequeType.INSTANT,
                info='', client_notify_url=''):
    # amount
    try:
        amount = Decimal(amount)
    except InvalidOperation:
        raise AmountValueError(amount)

    if amount <= 0:
        raise NonPositiveAmountError(amount)

    # valid_seconds
    try:
        valid_seconds = int(valid_seconds)
    except:
        raise ValueError('bad valid seconds.')

    if valid_seconds <= 0:
        raise ValueError('valid_seconds should be positive integer.')

    comments = "支票: %s" % info
    user_ids = [user_roles.from_user(from_id)]
    tx = create_transaction(channel.name, TransactionType.CHEQUE, amount, comments, user_ids, order_id=order_id)

    fields = {
        'tx_id': tx.id,
        'sn': tx.sn,
        'type': cheque_type,
        'from_id': from_id,
        'amount': amount,
        'expired_at': datetime.utcnow() + timedelta(seconds=valid_seconds),
        'signature': gen_signature(),
        'client_notify_url': client_notify_url
    }

    cheque_record = ChequeRecord(**fields)
    db.session.add(cheque_record)

    _draw_cheque(tx, cheque_record)

    return cheque_record


def cash_cheque(channel, to_id, cash_token):
    cheque_record = ChequeRecord.get_cheque_record_from_cash_token(cash_token)
    if cheque_record is None:
        raise BadCashChequeTokenError()

    tx = cheque_record.tx
    if tx.state == ChequeTxState.CANCELED:
        raise CashChequeError('cheque is canceled.')
    if tx.state == ChequeTxState.CASHED:
        raise CashChequeError('cheque is cashed.')
    if tx.state == ChequeTxState.EXPIRED or expire_cheque(tx, cheque_record):
        raise CashChequeError('cheque is expired.')

    _cash_cheque(cheque_record, to_id)
    return cheque_record


@transactional
def cancel_cheque(channel, user_id, sn):
    cheque_record = ChequeRecord.query.filter_by(from_id=user_id, sn=sn).first()
    if cheque_record is None:
        raise Exception('cheque not exists.')

    tx = cheque_record.tx
    if tx.state not in [ChequeTxState.CREATED, ChequeTxState.FROZEN]:
        raise Exception('invalid cheque state.')
    _cancel_cheque(tx, cheque_record)


@transactional
def list_cheque(channel, user_id):
    """
    default fetch user's valid cheques.
    :param channel:
    :param user_id:
    :return:
    """
    return ChequeRecord.query.filter_by(from_id=user_id).filter(ChequeRecord.created_on == ChequeRecord.updated_on).\
        filter(ChequeRecord.expired_at >= datetime.utcnow()).all()


@transactional
def expire_cheque(tx, cheque_record):
    if datetime.utcnow() > cheque_record.expired_at:
        if cheque_record.type == ChequeType.INSTANT:
            _do_expire_frozen_cheque(tx, cheque_record)
        elif cheque_record.type == ChequeType.LAZY:
            transit_transaction_state(tx.id, ChequeTxState.CREATED, ChequeTxState.EXPIRED)
        return True
    return False


@transactional
def _cancel_cheque(tx, cheque_record):
    if cheque_record.type == ChequeType.INSTANT:
        _do_cancel_frozen_cheque(tx, cheque_record)
    elif cheque_record.type == ChequeType.LAZY:
        transit_transaction_state(tx.id, ChequeTxState.CREATED, ChequeTxState.CANCELED)


@transactional
def _draw_cheque(tx, cheque_record):
    if cheque_record.type == ChequeType.INSTANT:
        event_ids = []
        event_id = zyt_bookkeeping(EventType.FREEZE, tx.sn, cheque_record.from_id, cheque_record.amount)
        event_ids.append(event_id)
        transit_transaction_state(tx.id, ChequeTxState.CREATED, ChequeTxState.FROZEN, event_ids)
    elif cheque_record.type == ChequeType.LAZY:
        pass


def _cash_cheque(cheque_record, to_id):
    from api_x.zyt.vas import NAME
    tx = cheque_record.tx
    with require_transaction_context():
        tx = update_transaction_info(tx.id, tx.sn, vas_name=NAME)
        if cheque_record.type == ChequeType.INSTANT:
            event_ids = transfer_frozen(tx.sn, cheque_record.from_id, to_id, cheque_record.amount)
            transit_transaction_state(tx.id, ChequeTxState.FROZEN, ChequeTxState.CASHED, event_ids)
        elif cheque_record.type == ChequeType.LAZY:
            event_ids = transfer(tx.sn, cheque_record.from_id, to_id, cheque_record.amount)
            transit_transaction_state(tx.id, ChequeTxState.CREATED, ChequeTxState.CASHED, event_ids)

        # update to id.
        add_tx_user(tx.id, user_roles.to_user(to_id))
        cheque_record.to_id = to_id
        db.session.add(cheque_record)

    # notify client.
    tx = get_tx_by_id(tx.id)
    _try_notify_client(tx, cheque_record)


def _try_notify_client(tx, cheque_record):
    from api_x.utils.notify import sign_and_notify_client
    url = cheque_record.client_notify_url
    if not url:
        return

    params = None
    if tx.state == ChequeTxState.CASHED:
        user_mapping = get_user_map_by_account_user_id(cheque_record.from_id)
        user_id = user_mapping.user_id
        params = {'code': 0, 'sn': tx.sn, 'user_id': user_id, 'amount': cheque_record.amount, 'order_id': tx.order_id}

    # notify
    sign_and_notify_client(url, params, tx.channel_name, task=tasks.cash_cheque_notify)


@transactional
def _do_cancel_frozen_cheque(tx, cheque_record):
    event_ids = []
    event_id = zyt_bookkeeping(EventType.UNFREEZE, tx.sn, cheque_record.from_id, cheque_record.amount)
    event_ids.append(event_id)
    transit_transaction_state(tx.id, ChequeTxState.FROZEN, ChequeTxState.CANCELED, event_ids)


@transactional
def _do_expire_frozen_cheque(tx, cheque_record):
    event_ids = []
    event_id = zyt_bookkeeping(EventType.UNFREEZE, tx.sn, cheque_record.from_id, cheque_record.amount)
    event_ids.append(event_id)
    transit_transaction_state(tx.id, ChequeTxState.FROZEN, ChequeTxState.EXPIRED, event_ids)


