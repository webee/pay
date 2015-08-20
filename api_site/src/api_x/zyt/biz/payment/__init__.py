# coding=utf-8
from __future__ import unicode_literals
from api_x.zyt.biz.commons import is_duplicated_notify

from flask import redirect
from api_x import db
from api_x.zyt.vas.bookkeep import bookkeeping
from api_x.zyt.user_mapping import get_system_account_user_id, get_channel, get_user_map_by_account_user_id
from api_x.constant import TransactionState, SECURE_USER_NAME, PaymentTransactionState
from api_x.zyt.vas import NAME as ZYT_NAME
from api_x.zyt.vas.models import EventType
from api_x.zyt.biz.transaction import create_transaction, transit_transaction_state, get_tx_by_sn, \
    update_transaction_info, get_tx_by_id
from api_x.zyt.biz.models import TransactionType, PaymentRecord, PaymentType
from api_x.zyt.biz.error import NonPositiveAmountError
from pytoolbox.util.dbs import require_transaction_context, transactional
from tools.mylog import get_logger


logger = get_logger(__name__)


def find_or_create_payment(payment_type, payer_id, payee_id, channel, order_id,
                           product_name, product_category, product_desc, amount,
                           client_callback_url, client_notify_url):
    """
    如果金额为0, 新建订单则直接失败
    如果已经有对应订单，则直接支付成功
    """
    payment_record = PaymentRecord.query.filter_by(channel_id=channel.id, order_id=order_id).first()
    if payment_record is None:
        if amount <= 0:
            raise NonPositiveAmountError(amount)

        payment_record = _create_payment(payment_type, payer_id, payee_id, channel, order_id,
                                         product_name, product_category, product_desc, amount,
                                         client_callback_url, client_notify_url)
    else:
        # update payment info, if not paid.
        with require_transaction_context():
            tx = get_tx_by_sn(payment_record.sn)
            if tx.state == PaymentTransactionState.CREATED:
                PaymentRecord.query.filter_by(id=payment_record.id) \
                    .update({'amount': amount,
                             'product_name': product_name,
                             'product_category': product_category,
                             'product_desc': product_desc})

            payment_record = PaymentRecord.query.get(payment_record.id)
    if payment_record.amount <= 0:
        from api_x.zyt import vas as zyt

        tx = update_transaction_info(payment_record.tx_id.id, zyt.NAME, payment_record.sn,
                                     PaymentTransactionState.CREATED)
        succeed_payment(zyt.NAME, payment_record)
    return payment_record


@transactional
def _create_payment(payment_type, payer_id, payee_id, channel, order_id,
                    product_name, product_category, product_desc, amount,
                    client_callback_url, client_notify_url):
    comments = "在线支付-{0}:{1}|{2}".format(channel.name, product_name, order_id)
    user_ids = [payer_id, payee_id]
    if payment_type == PaymentType.GUARANTEE:
        secure_user_id = get_system_account_user_id(SECURE_USER_NAME)
        user_ids.append(secure_user_id)
    tx_record = create_transaction(TransactionType.PAYMENT, amount, comments, user_ids)

    fields = {
        'tx_id': tx_record.id,
        'sn': tx_record.sn,
        'payer_id': payer_id,
        'payee_id': payee_id,
        'channel_id': channel.id,
        'order_id': order_id,
        'product_name': product_name,
        'product_category': product_category,
        'product_desc': product_desc,
        'amount': amount,
        'client_callback_url': client_callback_url,
        'client_notify_url': client_notify_url,
        'type': payment_type
    }

    payment_record = PaymentRecord(**fields)
    db.session.add(payment_record)

    return payment_record


def get_payment_by_channel_order_id(channel_id, order_id):
    return PaymentRecord.query.filter_by(channel_id=channel_id, order_id=order_id).first()


def get_payment_by_tx_id(tx_id):
    return PaymentRecord.query.filter_by(tx_id=tx_id).first()


def get_payment_by_sn(sn):
    return PaymentRecord.query.filter_by(sn=sn).first()


def get_payment_by_id(id):
    return PaymentRecord.query.get(id)


def get_tx_payment_by_sn(sn):
    return get_tx_by_sn(sn), get_payment_by_sn(sn)


@transactional
def succeed_payment(vas_name, payment_record):
    event_id = bookkeeping(EventType.TRANSFER_IN, payment_record.sn, payment_record.payee_id, vas_name,
                           payment_record.amount)
    transit_transaction_state(payment_record.tx_id, TransactionState.CREATED, TransactionState.SUCCESS, event_id)


@transactional
def secure_payment(vas_name, payment_record):
    secure_user_id = get_system_account_user_id(SECURE_USER_NAME)
    event_id = bookkeeping(EventType.TRANSFER_IN_FROZEN, payment_record.sn, secure_user_id, vas_name,
                           payment_record.amount)
    transit_transaction_state(payment_record.tx_id, TransactionState.CREATED, TransactionState.SECURED, event_id)


@transactional
def _confirm_payment(payment_record):
    secure_user_id = get_system_account_user_id(SECURE_USER_NAME)
    # 确认金额为订单金额 - 已退款金额
    amount = payment_record.amount - payment_record.refunded_amount
    event_id1 = bookkeeping(EventType.TRANSFER_OUT_FROZEN, payment_record.sn, secure_user_id, ZYT_NAME, amount)
    event_id2 = bookkeeping(EventType.TRANSFER_IN, payment_record.sn, payment_record.payee_id, ZYT_NAME, amount)

    transit_transaction_state(payment_record.tx_id, TransactionState.SECURED, TransactionState.SUCCESS,
                              [event_id1, event_id2])


@transactional
def fail_payment(payment_record):
    transit_transaction_state(payment_record.tx_id, TransactionState.CREATED, TransactionState.FAILED)


def handle_payment_result(is_success, sn, vas_name, vas_sn, data):
    """
    :param is_success: 是否成功
    :param sn: 订单号
    :param vas_name: 来源系统
    :param vas_sn: 来源系统订单号
    :param data: 数据
    :return:
    """
    tx, payment_record = get_tx_payment_by_sn(sn)

    if payment_record.client_callback_url:
        # FIXME: 为了兼容huodong的secured pay. 修改callback_url.
        channel = get_channel(payment_record.channel_id)
        if channel.name == 'lvye_huodong':
            user_mapping = get_user_map_by_account_user_id(payment_record.payer_id)
            url = '{0}?user_id={1}&order_id={2}&amount={3}&status=money_locked'.\
                format(payment_record.client_callback_url, user_mapping.user_id, payment_record.order_id, payment_record.amount)
            return redirect(url)
        return redirect(payment_record.client_callback_url)
    return redirect('/')


def handle_payment_notify(is_success, sn, vas_name, vas_sn, data):
    """
    :param is_success: 是否成功
    :param sn: 订单号
    :param vas_name: 来源系统
    :param vas_sn: 来源系统订单号
    :param data: 数据
    :return:
    """
    tx, payment_record = get_tx_payment_by_sn(sn)

    if is_duplicated_notify(tx, vas_name, vas_sn):
        return

    if _is_duplicated_payment(tx, payment_record, vas_name, vas_sn):
        # 重复支付
        # TODO, 退款到余额(短信通知)或者原路返回
        logger.warning('duplicated payment: [{0}], [{1}], [{2}, {3}]'.format(
            payment_record.vas_name, payment_record.vas_sn, vas_name, vas_sn))

    with require_transaction_context():
        tx = update_transaction_info(tx.id, vas_name, vas_sn, PaymentTransactionState.CREATED)
        if is_success:
            # 直付和担保付的不同操作
            if payment_record.type == PaymentType.DIRECT:
                succeed_payment(vas_name, payment_record)
            elif payment_record.type == PaymentType.GUARANTEE:
                secure_payment(vas_name, payment_record)
        else:
            fail_payment(payment_record)

    # notify client.
    tx = get_tx_by_id(tx.id)
    _try_notify_client(tx, payment_record)


def _try_notify_client(tx, payment_record):
    from api_x.utils.notify import notify_client
    url = payment_record.client_notify_url

    channel = get_channel(payment_record.channel_id)
    user_mapping = get_user_map_by_account_user_id(payment_record.payer_id)
    user_id = user_mapping.user_id

    # FIXME: 这里为了兼容之前活动平台的client_id=1, status='money_locked', methods加上'put'
    if tx.state in [PaymentTransactionState.SECURED, PaymentTransactionState.SUCCESS]:
        params = {'code': 0, 'client_id': '1', 'user_id': user_id, 'status': 'money_locked',
                  'channel_name': channel.name,
                  'order_id': payment_record.order_id, 'amount': payment_record.amount}
    elif tx.state == PaymentTransactionState.FAILED:
        params = {'code': 1, 'client_id': '1', 'user_id': user_id, 'status': 'money_locked',
                  'channel_name': channel.name,
                  'order_id': payment_record.order_id, 'amount': payment_record.amount}

    # FIXME: 为了兼容huodong的secured pay. 修改callback_url.
    if channel.name == 'lvye_huodong':
        url = '{0}?user_id={1}&order_id={2}&amount={3}&status=money_locked'. \
            format(payment_record.client_callback_url, user_id, payment_record.order_id, payment_record.amount)
    if not notify_client(url, params, methods=['put', 'post']):
        # other notify process.
        from api_x.task import tasks
        tasks.refund_notify.delay(url, params)


def _is_duplicated_payment(tx, payment_record, vas_name, vas_sn):
    if tx.state in [PaymentTransactionState.CREATED, PaymentTransactionState.FAILED]:
        return False

    return vas_name != payment_record.vas_name or vas_sn != payment_record.vas_sn


def confirm_payment(channel, order_id):
    payment_record = get_payment_by_channel_order_id(channel.id, order_id)
    if payment_record is not None and payment_record.type == PaymentType.GUARANTEE:
        _confirm_payment(payment_record)
