# coding=utf-8
from __future__ import unicode_literals

from api_x import db
from api_x.constant import TransferTxState
from api_x.zyt.user_mapping import get_user_domain_by_name
from api_x.zyt.vas.pattern import transfer
from api_x.zyt.biz.transaction import create_transaction, transit_transaction_state, update_transaction_info
from api_x.zyt.biz.models import TransactionType, TransferRecord
from api_x.zyt.biz.error import NonPositiveAmountError, AmountValueError
from api_x.zyt.biz import user_roles
from pytoolbox.util.dbs import transactional
from pytoolbox.util.log import get_logger
from decimal import Decimal, InvalidOperation


logger = get_logger(__name__)


def apply_to_transfer(channel, order_id, from_user_domain_name, from_user_id, to_user_domain_name, to_user_id, amount, info):
    from_user_domain = get_user_domain_by_name(from_user_domain_name)
    if from_user_domain is None:
        raise Exception("domain [{0}] not exists.".format(from_user_domain_name))
    from_user_map = from_user_domain.get_user_map(from_user_id)
    if from_user_map is None:
        raise Exception("from user with domain [{0}] user [{1}] not exists.".format(from_user_domain_name, from_user_id))

    to_user_domain = get_user_domain_by_name(to_user_domain_name)
    if to_user_domain is None:
        raise Exception("domain [{0}] not exists.".format(to_user_domain_name))
    to_user_map = to_user_domain.get_user_map(to_user_id)
    if to_user_map is None:
        raise Exception("to user with domain [{0}] user [{1}] not exists.".format(to_user_domain_name, to_user_id))

    return create_and_do_transfer(channel.name, order_id, from_user_map.account_user_id, to_user_map.account_user_id,
                                  amount, info)


@transactional
def create_and_do_transfer(channel_name, order_id, from_id, to_id, amount, info):
    try:
        amount = Decimal(amount)
    except InvalidOperation:
        raise AmountValueError(amount)

    if amount <= 0:
        raise NonPositiveAmountError(amount)

    comments = "转账: %s" % info
    user_ids = [user_roles.from_user(from_id), user_roles.to_user(to_id)]
    # TODO: 处理重复order_id的情况
    tx = create_transaction(channel_name, TransactionType.TRANSFER, amount, comments, user_ids, order_id=order_id)

    fields = {
        'tx_id': tx.id,
        'sn': tx.sn,
        'from_id': from_id,
        'to_id': to_id,
        'amount': amount,
    }

    transfer_record = TransferRecord(**fields)
    db.session.add(transfer_record)

    _do_transfer(tx, transfer_record)

    return tx


@transactional
def _do_transfer(tx, transfer_record):
    from api_x.zyt.vas import NAME
    event_ids = transfer(tx.sn, transfer_record.from_id, transfer_record.to_id, transfer_record.amount)
    transit_transaction_state(tx.id, tx.state, TransferTxState.SUCCESS, event_ids)

    update_transaction_info(tx.id, tx.sn, vas_name=NAME)
