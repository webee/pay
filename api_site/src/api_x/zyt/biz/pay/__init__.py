# coding=utf-8
from __future__ import unicode_literals
from decimal import InvalidOperation, Decimal

from api_x.zyt.biz.commons import is_duplicated_notify
from api_x.zyt.biz.pay.dba import get_payment_by_channel_order_id, get_payment_by_sn, get_payment_tx_by_sn
from api_x.zyt.biz.transaction.dba import get_tx_by_id
from api_x import db
from api_x.zyt.vas.bookkeep import bookkeeping
from api_x.zyt.vas.pattern import zyt_bookkeeping
from api_x.zyt.user_mapping import get_system_account_user_id, get_user_map_by_account_user_id
from api_x.constant import SECURE_USER_NAME, PaymentTxState, PaymentOriginType
from api_x.zyt.vas.models import EventType
from api_x.zyt.biz.transaction import create_transaction, transit_transaction_state, update_transaction_info
from api_x.zyt.biz.models import TransactionType, PaymentRecord, PaymentType, TransactionSnStack
from api_x.zyt.biz.error import NonPositiveAmountError, NegativeAmountError, AmountValueMissMatchError
from api_x.zyt.biz.error import TransactionNotFoundError, AmountValueError
from api_x.zyt.biz.transaction.error import TransactionStateError
from api_x.zyt.biz.models import DuplicatedPaymentRecord
from api_x.zyt.biz import user_roles
from pytoolbox.util.dbs import require_transaction_context, transactional
from pytoolbox.util.log import get_logger
from api_x.constant import PaymentChangeType
from api_x.config import etc as config
from api_x.task import tasks
from .error import AlreadyPaidError

logger = get_logger(__name__)


def find_or_create_payment(channel, payment_type, payer_id, payee_id, order_id,
                           product_name, product_category, product_desc, amount,
                           client_callback_url='', client_notify_url='', super_tx_id=None, origin=None):
    """
    如果金额为0, 则本次新建订单操作失败
    如果已经有对应订单，则直接支付成功
    """
    try:
        amount = Decimal(amount)
    except InvalidOperation:
        raise AmountValueError(amount)

    payment_record = PaymentRecord.query.filter_by(channel_id=channel.id, order_id=order_id, origin=origin).first()
    if payment_record is None:
        if amount <= 0:
            raise NonPositiveAmountError(amount)

        payment_record = _create_payment(channel, payment_type, payer_id, payee_id, order_id,
                                         product_name, product_category, product_desc, amount,
                                         client_callback_url, client_notify_url, super_tx_id=super_tx_id, origin=None)
    else:
        payment_record = _restart_payment(channel, payment_record, amount, product_name, product_category, product_desc)

    if payment_record.amount < 0:
        raise NegativeAmountError(payment_record.amount)

    if payment_record.amount == 0:
        # 直接成功
        from api_x.zyt import vas as zyt

        tx = update_transaction_info(payment_record.tx_id, payment_record.sn,
                                     vas_name=zyt.NAME, state=PaymentTxState.CREATED)
        succeed_payment(zyt.NAME, tx, payment_record)
    return payment_record


def is_payment_need_change(record, is_amount_changed, is_changed):
    if is_amount_changed:
        change = PaymentChangeType.AMOUNT
        return change
    if is_changed:
        change = PaymentChangeType.INFO
        return change
    from datetime import datetime

    if record.tried_times >= config.Biz.PAYMENT_MAX_TRIAL_TIMES:
        return PaymentChangeType.EXPIRED

    d = datetime.utcnow() - record.updated_on
    s = d.total_seconds()
    if s >= config.Biz.PAYMENT_MAX_VALID_SECONDS:
        return PaymentChangeType.EXPIRED


@transactional
def _restart_payment(channel, payment_record, amount, product_name, product_category, product_desc):
    from ..utils import generate_sn

    tx = payment_record.tx
    if not in_to_pay_state(tx.state, exclude=[PaymentTxState.PAID_OUT]):
        raise AlreadyPaidError(payment_record.order_id)

    is_changed = False
    is_amount_changed = False
    # 更新订单相关信息
    if tx.state in [PaymentTxState.CREATED, PaymentTxState.FAILED]:
        is_amount_changed = payment_record.amount != amount
        is_changed = is_changed or is_amount_changed
        payment_record.amount = amount

        is_changed = is_changed or payment_record.product_name != product_name[:150]
        payment_record.product_name = product_name[:150]

        is_changed = is_changed or payment_record.product_category != product_category[:50]
        payment_record.product_category = product_category[:50]

        is_changed = is_changed or payment_record.product_desc != product_desc[:350]
        payment_record.product_desc = product_desc[:350]

        tx.amount = amount
        tx.comments = "支付-{0}".format(product_name)

    change = is_payment_need_change(payment_record, is_amount_changed, is_changed)
    if change is not None:
        # push old sn to stack.
        tx_sn_stack = TransactionSnStack(tx_id=tx.id, sn=tx.sn, generated_on=tx.updated_on, state=tx.state, change=change)
        db.session.add(tx_sn_stack)

        # new sn.
        tx.sn = generate_sn(payment_record.payer_id)
        payment_record.sn = tx.sn
        payment_record.tried_times = 0

    # 如果之前失败了，则从这里重新开始
    if tx.state == PaymentTxState.FAILED:
        tx.state = PaymentTxState.CREATED

    tx.tried_times += 1
    payment_record.tried_times += 1
    db.session.add(tx)
    db.session.add(payment_record)
    return payment_record


@transactional
def _create_payment(channel, payment_type, payer_id, payee_id, order_id,
                    product_name, product_category, product_desc, amount,
                    client_callback_url, client_notify_url, super_tx_id=None, origin=None):
    comments = "支付-{0}".format(product_name)
    user_ids = [user_roles.from_user(payer_id), user_roles.to_user(payee_id)]
    if payment_type == PaymentType.GUARANTEE:
        secure_user_id = get_system_account_user_id(SECURE_USER_NAME)
        user_ids.append(user_roles.guaranteed_by(secure_user_id))
    tx = create_transaction(channel.name, TransactionType.PAYMENT, amount, comments, user_ids,
                            order_id=order_id, super_id=super_tx_id)

    fields = {
        'tx_id': tx.id,
        'sn': tx.sn,
        'payer_id': payer_id,
        'payee_id': payee_id,
        'channel_id': channel.id,
        'order_id': order_id,
        'origin': origin,
        'product_name': product_name,
        'product_category': product_category,
        'product_desc': product_desc,
        'amount': amount,
        'real_amount': amount,
        'client_callback_url': client_callback_url,
        'client_notify_url': client_notify_url,
        'type': payment_type
    }

    payment_record = PaymentRecord(**fields)
    db.session.add(payment_record)

    return payment_record


@transactional
def succeed_paid_out(vas_name, tx, payer_id, amount):
    event_id = bookkeeping(EventType.TRANSFER_OUT, tx.sn, payer_id, vas_name, amount)
    transit_transaction_state(tx.id, PaymentTxState.CREATED, PaymentTxState.PAID_OUT, event_id)


def in_to_pay_state(state, exclude=None):
    # 等待支付状态
    if exclude and state in exclude:
        return False

    return state in [PaymentTxState.CREATED, PaymentTxState.FAILED, PaymentTxState.PAID_OUT]


@transactional
def _record_and_refund_duplicate_payment(vas_name, vas_sn, tx, payment_record):
    # 自动退款
    from api_x.zyt.biz.refund import create_and_request_refund

    try:
        refund_record = create_and_request_refund(tx.channel, tx, payment_record.paid_amount, '')
    except Exception as e:
        msg = "duplicated payment [{0}] refund error: [{1}]".format(tx.sn, e.message)
        logger.warn(msg)

    duplicate_payment_record = DuplicatedPaymentRecord(tx_id=tx.id, sn=tx.sn, vas_name=vas_name, vas_sn=vas_sn,
                                                       source=TransactionType.PAYMENT)
    db.session.add(duplicate_payment_record)


@transactional
def handle_duplicate_payment(vas_name, vas_sn, tx, payment_record):
    from api_x.zyt.biz import utils
    # 创建重复支付交易
    amount = payment_record.real_amount
    order_id = utils.generate_order_id(tx.id)
    product_name = "重复支付: " + payment_record.product_name
    product_desc = "重复支付: order_id: [{0}]".format(payment_record.order_id)
    dup_payment_record = find_or_create_payment(tx.channel, payment_record.type,
                                                payment_record.payer_id, payment_record.payee_id, order_id,
                                                product_name, '重复支付', product_desc, amount,
                                                super_tx_id=tx.id, origin=PaymentOriginType.DUPLICATE)
    dup_payment_tx = dup_payment_record.tx
    # handle right now!
    handle_payment_notify(True, dup_payment_tx.sn, vas_name, vas_sn, amount)

    # 记录重复支付并自动原路返回此交易
    _record_and_refund_duplicate_payment(vas_name, vas_sn, dup_payment_tx, dup_payment_record)


@transactional
def succeed_payment(vas_name, tx, payment_record, state=PaymentTxState.SUCCESS, bk=None):
    payee_id = payment_record.payee_id
    amount = payment_record.real_amount
    if not in_to_pay_state(tx.state):
        raise TransactionStateError(msg='state error: [{0}]'.format(tx.state))

    if amount == 0:
        # 不用记账
        event_id = None
    else:
        event_id = bk() if bk else bookkeeping(EventType.TRANSFER_IN, tx.sn, payee_id, vas_name, amount)
    transit_transaction_state(tx.id, tx.state, state, event_id)


@transactional
def secure_payment(vas_name, tx, payment_record):
    def bk(sn, amount):
        secure_user_id = get_system_account_user_id(SECURE_USER_NAME)
        return bookkeeping(EventType.TRANSFER_IN_FROZEN, sn, secure_user_id, vas_name, amount)

    succeed_payment(vas_name, tx, payment_record, state=PaymentTxState.SECURED, bk=bk)


@transactional
def _confirm_payment(payment_record):
    secure_user_id = get_system_account_user_id(SECURE_USER_NAME)
    # 确认金额为订单金额 - 已退款金额
    amount = payment_record.amount - payment_record.refunded_amount
    event_id1 = zyt_bookkeeping(EventType.TRANSFER_OUT_FROZEN, payment_record.sn, secure_user_id, amount)
    event_id2 = zyt_bookkeeping(EventType.TRANSFER_IN, payment_record.sn, payment_record.payee_id, amount)

    transit_transaction_state(payment_record.tx_id, PaymentTxState.SECURED, PaymentTxState.SUCCESS,
                              [event_id1, event_id2])


@transactional
def fail_payment(payment_record):
    transit_transaction_state(payment_record.tx_id, PaymentTxState.CREATED, PaymentTxState.FAILED)


@transactional
def handle_paid_out(vas_name, sn, payer_id, amount, notify_handle=None):
    tx = get_payment_tx_by_sn(sn)
    succeed_paid_out(vas_name, tx, payer_id, amount)

    # FIXME: 这里按逻辑应该用异步的, 但是由于两方为同一个系统，所以直接同步处理了
    if notify_handle is not None:
        notify_handle(True)


def handle_payment_notify(is_success, sn, vas_name, vas_sn, amount, data=None):
    """
    :param is_success: 是否成功
    :param sn: 订单号
    :param vas_name: 来源系统
    :param vas_sn: 来源系统订单号
    :param data: 数据
    :return:
    """
    logger.info('receive payment notify: [{0}], [{1}], [{2}], [{3}], [{4}]'.format(is_success, sn, vas_name, vas_sn, amount))
    tx = get_payment_tx_by_sn(sn)
    payment_record = tx.record

    if amount != payment_record.real_amount:
        # 单次支付的金额一定要完全一致
        raise AmountValueMissMatchError(payment_record.amount, amount)

    if is_duplicated_notify(tx, vas_name, vas_sn):
        return

    with require_transaction_context():
        if is_success:
            # update paid amount
            payment_record.add_paid(amount)

            if _is_duplicated_payment(tx, vas_name, vas_sn):
                # 重复支付
                logger.warning('duplicated payment: [{0}, {1}], [{2}, {3}], [{4}]'.format(tx.vas_name, tx.vas_sn,
                                                                                          vas_name, vas_sn, amount))
                handle_duplicate_payment(vas_name, vas_sn, tx, payment_record)
                return

            # 直付和担保付的不同操作
            if payment_record.type == PaymentType.DIRECT:
                succeed_payment(vas_name, tx, payment_record)
            elif payment_record.type == PaymentType.GUARANTEE:
                secure_payment(vas_name, tx, payment_record)
        else:
            fail_payment(payment_record)
        tx = update_transaction_info(tx.id, vas_sn, vas_name=vas_name)

    # notify client.
    tx = get_tx_by_id(tx.id)
    _try_notify_client(tx, payment_record)


def _try_notify_client(tx, payment_record):
    from api_x.utils.notify import sign_and_notify_client

    url = payment_record.client_notify_url
    if not url:
        return

    user_mapping = get_user_map_by_account_user_id(payment_record.payer_id)
    user_id = user_mapping.user_id

    params = None
    if tx.state in [PaymentTxState.SECURED, PaymentTxState.SUCCESS]:
        params = {'code': 0, 'user_id': user_id, 'sn': payment_record.sn,
                  'order_id': payment_record.order_id, 'amount': payment_record.amount}
    elif tx.state == PaymentTxState.FAILED:
        params = {'code': 1, 'user_id': user_id, 'sn': payment_record.sn,
                  'order_id': payment_record.order_id, 'amount': payment_record.amount}

    # notify
    sign_and_notify_client(url, params, tx.channel_name, task=tasks.pay_notify)


def _is_duplicated_payment(tx, vas_name, vas_sn):
    if in_to_pay_state(tx.state):
        return False

    if tx.vas_name is None or tx.vas_sn is None:
        return False

    return vas_name != tx.vas_name or vas_sn != tx.vas_sn


def confirm_payment(channel, order_id):
    payment_record = get_payment_by_channel_order_id(channel.id, order_id)
    if payment_record is None or payment_record.type != PaymentType.GUARANTEE:
        raise TransactionNotFoundError('guarantee payment tx channel=[{0}], order_id=[{1}] not found.'.format(channel.name, order_id))

    tx = get_tx_by_id(payment_record.tx_id)
    # 只有担保才能确认
    # 另外，担保可能发生退款的情况，则需要退款完成之后再次确认。
    if tx.state == PaymentTxState.SECURED:
        _confirm_payment(payment_record)
    elif tx.state == PaymentTxState.REFUNDING:
        msg = 'payment is REFUNDING, try again later.'
        logger.warn(msg)
        raise TransactionStateError(msg)
    else:
        logger.warn('payment state should be SECURED.')
