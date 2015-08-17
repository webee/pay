# coding=utf-8
from __future__ import unicode_literals

from flask import redirect
from api_x import db
from api_x.zyt.vas.bookkeep import bookkeeping
from api_x.zyt.user_mapping import get_channel_info, get_system_account_user_id
from api_x.constant import TransactionState, SECURE_USER_NAME, PaymentTransactionState
from api_x.dbs import transactional
from api_x.zyt.vas import NAME as ZYT_NAME
from api_x.zyt.vas.models import EventType
from api_x.zyt.biz.transaction import create_transaction, transit_transaction_state, get_tx_by_sn
from api_x.zyt.biz.models import TransactionType, PaymentRecord, PaymentType
from api_x.dbs import require_transaction_context
from api_x.zyt.biz.error import NonPositiveAmountError
from tools.mylog import get_logger


logger = get_logger(__name__)


@transactional
def create_payment(payment_type, payer_id, payee_id, channel_id, order_id,
                   product_name, product_category, product_desc, amount,
                   client_callback_url, client_notify_url):
    channel = get_channel_info(channel_id)
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
        'channel_id': channel_id,
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


def find_or_create_payment(payment_type, payer_id, payee_id, channel_id, order_id,
                           product_name, product_category, product_desc, amount,
                           client_callback_url, client_notify_url):
    """
    如果金额为0, 新建订单则直接失败
    如果已经有对应订单，则直接支付成功
    """
    payment_record = PaymentRecord.query.filter_by(channel_id=channel_id, order_id=order_id).first()
    if payment_record is None:
        if amount <= 0:
            raise NonPositiveAmountError(amount)

        payment_record = create_payment(payment_type, payer_id, payee_id, channel_id, order_id,
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
        payment_record = update_payment_info(payment_record.id, zyt.NAME, '')
        succeed_payment(zyt.NAME, payment_record)
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
def update_payment_info(payment_id, vas_name, vas_sn):
    payment_record = PaymentRecord.query.get(payment_id)
    payment_record.vas_name = vas_name
    payment_record.vas_sn = vas_sn

    db.session.add(payment_record)

    return payment_record


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
    trx, payment_record = get_tx_payment_by_sn(sn)

    if payment_record.client_callback_url:
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
    from ..transaction import TransactionStateError

    tx, payment_record = get_tx_payment_by_sn(sn)

    try:
        with require_transaction_context():
            if is_success:
                # 直付和担保付的不同操作
                if payment_record.type == PaymentType.DIRECT:
                    succeed_payment(vas_name, payment_record)
                elif payment_record.type == PaymentType.GUARANTEE:
                    secure_payment(vas_name, payment_record)
            else:
                fail_payment(payment_record)
            payment_record = update_payment_info(payment_record.id, vas_name, vas_sn)
    except TransactionStateError as e:
        logger.exception(e)
        # 重复通知，或者不同支付方式重复支付
        if tx.state in [PaymentTransactionState.SUCCESS, PaymentTransactionState.SECURED]:
            if payment_record.vas_name != vas_name:
                # 重复支付
                # TODO, 退款到余额(短信通知)或者原路返回
                logger.warning('duplicated payment: [{0}], [{1}]'.format(payment_record.vas_name, vas_name))
    # TODO
    # notify

    return True


def confirm_payment(channel_id, order_id):
    payment_record = get_payment_by_channel_order_id(channel_id, order_id)
    if payment_record is not None and payment_record.type == PaymentType.GUARANTEE:
        _confirm_payment(payment_record)
