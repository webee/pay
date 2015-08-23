# coding=utf-8
from __future__ import unicode_literals
from api_x.zyt.biz.commons import is_duplicated_notify
from api_x.zyt.biz.transaction.dba import get_tx_by_id, get_tx_by_sn

from flask import redirect
from api_x import db
from api_x.zyt.vas.bookkeep import bookkeeping
from api_x.zyt.user_mapping import get_system_account_user_id, get_channel, get_user_map_by_account_user_id, \
    get_channel_by_name
from api_x.constant import TransactionState, SECURE_USER_NAME, PaymentTransactionState
from api_x.zyt.vas import NAME as ZYT_NAME
from api_x.zyt.vas.models import EventType
from api_x.zyt.biz.transaction import create_transaction, transit_transaction_state, update_transaction_info
from api_x.zyt.biz.models import TransactionType, PaymentRecord, PaymentType
from api_x.zyt.biz.error import NonPositiveAmountError
from api_x.zyt.biz.error import TransactionNotFoundError
from api_x.zyt.biz.transaction.error import TransactionStateError
from api_x.zyt.biz.models import UserRole
from pytoolbox.util.dbs import require_transaction_context, transactional
from pytoolbox.util.log import get_logger
from api_x.utils import response


logger = get_logger(__name__)


def find_or_create_payment(channel, payment_type, payer_id, payee_id, order_id,
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

        payment_record = _create_payment(channel, payment_type, payer_id, payee_id, order_id,
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
def _create_payment(channel, payment_type, payer_id, payee_id, order_id,
                    product_name, product_category, product_desc, amount,
                    client_callback_url, client_notify_url):
    comments = "在线支付-{0}:{0}|{1}".format(channel.desc, product_name, order_id)
    user_ids = [(payer_id, UserRole.FROM), (payee_id, UserRole.TO)]
    if payment_type == PaymentType.GUARANTEE:
        secure_user_id = get_system_account_user_id(SECURE_USER_NAME)
        user_ids.append((secure_user_id, UserRole.GUARANTOR))
    tx_record = create_transaction(channel.name, TransactionType.PAYMENT, amount, comments, user_ids)

    fields = {
        'tx_id': tx_record.id,
        'sn': tx_record.sn,
        'payer_id': payer_id,
        'payee_id': payee_id,
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
    from flask import url_for
    tx, payment_record = get_tx_payment_by_sn(sn)
    client_callback_url = payment_record.client_callback_url

    if client_callback_url and is_success:
        channel = get_channel_by_name(tx.channel_name)
        user_mapping = get_user_map_by_account_user_id(payment_record.payer_id)
        user_id = user_mapping.user_id
        params = {'code': 0, 'user_id': user_id, 'sn': payment_record.sn,
                  'channel_name': channel.name,
                  'order_id': payment_record.order_id, 'amount': payment_record.amount}
        return response.submit_form(client_callback_url, params)
    code = 0 if is_success else 1
    return redirect(url_for('biz_entry.pay_result', sn=sn, vas_name=vas_name, code=code, vas_sn=vas_sn))


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
        logger.warning('duplicated payment: [{0}], [{1}], [{2}, {3}]'.format(payment_record.vas_name,
                                                                             payment_record.vas_sn, vas_name, vas_sn))

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
    from api_x.utils.notify import sign_and_notify_client

    url = payment_record.client_notify_url

    channel = get_channel_by_name(tx.channel_name)
    user_mapping = get_user_map_by_account_user_id(payment_record.payer_id)
    user_id = user_mapping.user_id

    params = None
    if tx.state in [PaymentTransactionState.SECURED, PaymentTransactionState.SUCCESS]:
        params = {'code': 0, 'user_id': user_id, 'sn': payment_record.sn,
                  'channel_name': channel.name,
                  'order_id': payment_record.order_id, 'amount': payment_record.amount}
    elif tx.state == PaymentTransactionState.FAILED:
        params = {'code': 1, 'user_id': user_id, 'sn': payment_record.sn,
                  'channel_name': channel.name,
                  'order_id': payment_record.order_id, 'amount': payment_record.amount}

    if params and not sign_and_notify_client(url, channel.name, params):
        # other notify process.
        from api_x.task import tasks

        tasks.refund_notify.delay(url, params)


def _is_duplicated_payment(tx, payment_record, vas_name, vas_sn):
    if tx.state in [PaymentTransactionState.CREATED, PaymentTransactionState.FAILED]:
        return False

    return vas_name != payment_record.vas_name or vas_sn != payment_record.vas_sn


def confirm_payment(channel, order_id):
    payment_record = get_payment_by_channel_order_id(channel.id, order_id)
    if payment_record is None or payment_record.type != PaymentType.GUARANTEE:
        raise TransactionNotFoundError('tx channel={0}, order_id={1} not found.'.format(channel.name, order_id))

    tx = get_tx_by_id(payment_record.tx_id)
    if tx.state != PaymentTransactionState.SECURED:
        raise TransactionStateError('payment state must be SECURED.')

    _confirm_payment(payment_record)
