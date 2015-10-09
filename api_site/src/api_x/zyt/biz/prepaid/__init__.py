# coding=utf-8
from __future__ import unicode_literals
from api_x.zyt.biz.commons import is_duplicated_notify
from api_x.zyt.biz.transaction.dba import get_tx_by_id, get_tx_by_sn

from flask import redirect
from api_x import db
from api_x.zyt.vas.bookkeep import bookkeeping
from api_x.zyt.user_mapping import get_user_map_by_account_user_id
from api_x.constant import PrepaidTxState
from api_x.zyt.vas.models import EventType
from api_x.zyt.biz.transaction import create_transaction, transit_transaction_state, update_transaction_info
from api_x.zyt.biz.models import TransactionType, PrepaidRecord
from api_x.zyt.biz.error import NonPositiveAmountError
from api_x.zyt.biz.models import DuplicatedPaymentRecord
from api_x.zyt.biz import user_roles
from pytoolbox.util.dbs import require_transaction_context, transactional
from pytoolbox.util.log import get_logger
from api_x.config import etc as config
from pytoolbox.util.urls import build_url
from api_x.task import tasks


logger = get_logger(__name__)


@transactional
def create_prepaid(channel, order_id, to_id, amount, client_callback_url, client_notify_url):
    if amount <= 0:
        raise NonPositiveAmountError(amount)

    comments = "充值"
    user_ids = [user_roles.to_user(to_id)]
    tx = create_transaction(channel.name, TransactionType.PREPAID, amount, comments, user_ids, order_id=order_id)

    fields = {
        'tx_id': tx.id,
        'sn': tx.sn,
        'to_id': to_id,
        'amount': amount,
        'client_callback_url': client_callback_url,
        'client_notify_url': client_notify_url
    }

    prepaid_record = PrepaidRecord(**fields)
    db.session.add(prepaid_record)

    return prepaid_record


@transactional
def succeed_prepaid(vas_name, tx, prepaid_record):
    event_id = bookkeeping(EventType.TRANSFER_IN, tx.sn, prepaid_record.to_id, vas_name, prepaid_record.amount)
    transit_transaction_state(tx.id, tx.state, PrepaidTxState.SUCCESS, event_id)


@transactional
def fail_prepaid(tx):
    transit_transaction_state(tx.id, PrepaidTxState.CREATED, PrepaidTxState.FAILED)


@transactional
def handle_duplicate_pay(vas_name, vas_sn, tx, prepaid_record):
    """处理充值时的重复支付"""
    event_id = bookkeeping(EventType.TRANSFER_IN, tx.sn, prepaid_record.to_id, vas_name,
                           prepaid_record.amount)
    # 交易总金额增加
    tx.amount += prepaid_record.amount
    db.session.add(tx)

    # 不改变状态，只是添加一条关联event
    transit_transaction_state(prepaid_record.tx_id, tx.state, tx.state, event_id)

    # 添加一条重复支付记录
    duplicate_payment_record = DuplicatedPaymentRecord(tx_id=tx.id,
                                                       sn=tx.sn, event_id=event_id, vas_name=vas_name, vas_sn=vas_sn,
                                                       source=TransactionType.PREPAID)
    db.session.add(duplicate_payment_record)


def handle_prepaid_result(is_success, sn, vas_name, vas_sn, data):
    """
    :param is_success: 是否成功
    :param sn: 订单号
    :param vas_name: 来源系统
    :param vas_sn: 来源系统订单号
    :param data: 数据
    :return:
    """
    tx = get_tx_by_sn(sn)
    prepaid_record = tx.record

    client_callback_url = prepaid_record.client_callback_url

    code = 0 if is_success else 1
    if client_callback_url:
        from api_x.utils.notify import sign_and_return_client_callback
        user_mapping = get_user_map_by_account_user_id(prepaid_record.to_id)
        user_id = user_mapping.user_id
        params = {'code': code, 'user_id': user_id, 'sn': sn, 'amount': prepaid_record.amount}
        return sign_and_return_client_callback(client_callback_url, tx.channel_name, params, method="POST")

    from flask import url_for
    return redirect(config.HOST_URL + build_url(url_for('biz_entry.pay_result',
                                                        source=TransactionType.PREPAID, sn=sn, vas_name=vas_name),
                                                code=code, vas_sn=vas_sn))


def handle_prepaid_notify(is_success, sn, vas_name, vas_sn, data):
    """
    :param is_success: 是否成功
    :param sn: 订单号
    :param vas_name: 来源系统
    :param vas_sn: 来源系统订单号
    :param data: 数据
    :return:
    """
    tx = get_tx_by_sn(sn)
    prepaid_record = tx.record

    if is_duplicated_notify(tx, vas_name, vas_sn):
        return

    if _is_duplicated_prepaid(tx, vas_name, vas_sn):
        # 重复支付
        logger.warning('duplicated prepaid: [{0}], [{1}], [{2}, {3}]'.format(prepaid_record.vas_name,
                                                                             prepaid_record.vas_sn, vas_name, vas_sn))
        handle_duplicate_pay(vas_name, vas_sn, tx, prepaid_record)
        return

    with require_transaction_context():
        tx = update_transaction_info(tx.id, vas_sn, vas_name=vas_name)
        if is_success:
            succeed_prepaid(vas_name, tx, prepaid_record)
        else:
            fail_prepaid(tx)

    # notify client.
    tx = get_tx_by_id(tx.id)
    _try_notify_client(tx, prepaid_record)


def _try_notify_client(tx, prepaid_record):
    from api_x.utils.notify import sign_and_notify_client

    url = prepaid_record.client_notify_url

    user_mapping = get_user_map_by_account_user_id(prepaid_record.to_id)
    user_id = user_mapping.user_id

    params = None
    if tx.state == PrepaidTxState.SUCCESS:
        params = {'code': 0, 'user_id': user_id, 'sn': prepaid_record.sn, 'amount': prepaid_record.amount}
    elif tx.state == PrepaidTxState.FAILED:
        params = {'code': 1, 'user_id': user_id, 'sn': prepaid_record.sn, 'amount': prepaid_record.amount}

    # notify
    sign_and_notify_client(url, params, tx.channel_name, task=tasks.prepaid_notify)


def _is_duplicated_prepaid(tx, vas_name, vas_sn):
    if tx.state in [PrepaidTxState.CREATED, PrepaidTxState.FAILED]:
        return False

    return vas_name != tx.vas_name or vas_sn != tx.vas_sn
