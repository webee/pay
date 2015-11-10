# coding=utf-8
from __future__ import unicode_literals

from api_x import db
from api_x.constant import TransferTxState
from api_x.zyt.vas.pattern import transfer
from api_x.zyt.biz.transaction import create_transaction, transit_transaction_state
from api_x.zyt.biz.models import TransactionType, TransferRecord
from api_x.zyt.biz.error import NonPositiveAmountError, AmountValueError
from api_x.zyt.biz import user_roles
from pytoolbox.util.dbs import transactional
from pytoolbox.util.log import get_logger
from decimal import Decimal, InvalidOperation


logger = get_logger(__name__)


@transactional
def apply_to_transfer(channel, order_id, from_id, to_id, amount, info):
    try:
        amount = Decimal(amount)
    except InvalidOperation:
        raise AmountValueError(amount)

    if amount <= 0:
        raise NonPositiveAmountError(amount)

    comments = "转账: %s" % info
    user_ids = [user_roles.from_user(from_id), user_roles.to_user(to_id)]
    # TODO: 处理重复order_id的情况
    tx = create_transaction(channel.name, TransactionType.TRANSFER, amount, comments, user_ids, order_id=order_id)

    fields = {
        'tx_id': tx.id,
        'sn': tx.sn,
        'from_id': from_id,
        'to_id': to_id,
        'amount': amount,
    }

    transfer_record = TransferRecord(**fields)
    db.session.add(transfer_record)

    do_transfer(tx, transfer_record)

    return tx


@transactional
def do_transfer(tx, transfer_record):
    event_ids = transfer(tx.sn, transfer_record.from_id, transfer_record.to_id, transfer_record.amount)
    transit_transaction_state(tx.id, tx.state, TransferTxState.SUCCESS, event_ids)
