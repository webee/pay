# coding=utf-8
from __future__ import unicode_literals
from datetime import datetime
from decimal import Decimal, InvalidOperation

import requests
from api.util.ipay import transaction
from tools.dbe import db_transactional, db_operate
from api.util import id
from api import constant
from api.util.bookkeeping import bookkeeping, Event
from tools.mylog import get_logger
from tools.utils import to_int
from .bankcard import get_bankcard
from tools.lock import require_user_account_lock, GetLockError, GetLockTimeoutError
from api.util.ipay.transaction import notification
from tools.utils import to_float
from . import account

logger = get_logger(__name__)


class NoBankcardFoundError(Exception):
    def __init__(self, account_id, bankcard_id):
        message = "Cannot find bankcard with [account_id={0}, bankcard_id={1}].".format(account_id, bankcard_id)
        super(NoBankcardFoundError, self).__init__(message)


class AmountValueError(Exception):
    def __init__(self, amount):
        message = "amount value error: [{0}]".format(amount)
        super(AmountValueError, self).__init__(message)


class AmountNotPositiveError(Exception):
    def __init__(self, amount):
        message = "amount must be positive: [{0}]".format(amount)
        super(AmountNotPositiveError, self).__init__(message)


class InsufficientBalanceError(Exception):
    def __init__(self):
        message = "insufficient balance error."
        super(InsufficientBalanceError, self).__init__(message)


class CreateWithDrawOrderError(Exception):
    def __init__(self):
        message = "create withdraw failed."
        super(CreateWithDrawOrderError, self).__init__(message)


class WithDrawFailedError(Exception):
    def __init__(self, order_id):
        message = "withdraw failed: [{0}].".format(order_id)
        super(WithDrawFailedError, self).__init__(message)
        self.order_id = order_id


def withdraw_transaction(account_id, bankcard_id, amount, callback_url):
    bankcard = get_bankcard(account_id, to_int(bankcard_id))
    if bankcard is None:
        raise NoBankcardFoundError(account_id, bankcard_id)

    try:
        amount_value = Decimal(amount)
    except InvalidOperation:
        raise AmountValueError(amount)

    if amount_value <= 0:
        raise AmountNotPositiveError(amount_value)

    order_id = _withdraw(account_id, bankcard.id, amount_value, callback_url)

    try:
        _apply_for_withdraw(order_id, amount, bankcard)
    except WithDrawFailedError as e:
        _withdraw_request_failed(order_id)
        raise e

    return order_id


def _apply_for_withdraw(order_id, amount, bankcard):
    order_info = "自游通提现"
    notify_url = transaction.generate_pay_to_bankcard_notification_url(order_id)
    try:
        _ = transaction.pay_to_bankcard(order_id, amount, order_info, notify_url, bankcard)
    except Exception as e:
        logger.warn(e.message)
        raise WithDrawFailedError(order_id)


@db_transactional
def _withdraw(db, account_id, bankcard_id, amount, callback_url):
    """ 新建提现订单并冻结金额
    :param account_id: 提现账户id
    :param bankcard_id: 银行卡id
    :param amount: 提现金额
    :param callback_url: 请求方回调通知url
    :return:
    """
    try:
        with require_user_account_lock(account_id, 'cash') as _:
            balance = account.get_cash_balance(account_id)
            if amount > balance:
                raise InsufficientBalanceError()
            order_id = _create_withdraw_order(db, account_id, bankcard_id, amount, callback_url)
            withdraw_order = get_withdraw_order(db, order_id)
            _frozen_withdraw_cash(withdraw_order)

            return order_id
    except GetLockError:
        raise CreateWithDrawOrderError()
    except GetLockTimeoutError:
        raise CreateWithDrawOrderError()


def _create_withdraw_order(db, account_id, bankcard_id, amount, callback_url):
    order_id = id.withdraw_id(account_id)
    fields = {
        'id': order_id,
        'account_id': account_id,
        'bankcard_id': bankcard_id,
        'amount': amount,
        'created_on': datetime.now(),
        'callback_url': callback_url,
        'result': constant.WithdrawResult.FROZEN
    }

    db.insert('withdraw', fields)

    return order_id


@db_transactional
def _withdraw_request_failed(db, order_id):
    withdraw_order = get_withdraw_order(db, order_id)
    if withdraw_order and withdraw_order.result == constant.WithdrawResult.FROZEN:
        db.execute("update withdraw set result=%(result)s, failure_info=%(failure_info)s, ended_on=%(ended_on)s"
                   "where id=%(id)s", result=constant.WithdrawResult.FAILED,
                   failure_info='withdraw request failed.', ended_on=datetime.now(), id=order_id)

        _unfrozen_back_withdraw_cash(withdraw_order)


@db_transactional
def _succeed_withdraw(db, withdraw_order, paybill_id, settle_date):
    db.execute("""
              update withdraw set paybill_id=%(paybill_id)s, result=%(result)s,
              settle_date=%(settle_date)s, ended_on=%(ended_on)s where id=%(id)s
              """, paybill_id=paybill_id, result=constant.WithdrawResult.SUCCESS, settle_date=settle_date,
               ended_on=datetime.now(), id=withdraw_order['id'])

    _unfrozen_out_withdraw_cash(withdraw_order)


@db_transactional
def _fail_withdraw(db, withdraw_order, paybill_id, failure_info):
    db.execute("""
              update withdraw set paybill_id=%(paybill_id)s, result=%(result)s,
              failure_info=%(failure_info)s, ended_on=%(ended_on)s where id=%(id)s
              """, paybill_id=paybill_id, result=constant.WithdrawResult.FAILED,
               failure_info=failure_info, ended_on=datetime.now(),
               id=withdraw_order['id'])

    _unfrozen_back_withdraw_cash(withdraw_order)


def _frozen_withdraw_cash(withdraw_order):
    event = Event(withdraw_order['account_id'], constant.SourceType.WITHDRAW, constant.WithdrawStep.FROZEN,
                  withdraw_order['id'], withdraw_order['amount'])
    bookkeeping(event, '+frozen', '-cash')


def _unfrozen_back_withdraw_cash(withdraw_order):
    event = Event(withdraw_order['account_id'], constant.SourceType.WITHDRAW, constant.WithdrawStep.FAILED,
                  withdraw_order['id'], withdraw_order['amount'])
    bookkeeping(event, '-frozen', '+cash')


def _unfrozen_out_withdraw_cash(withdraw_order):
    event = Event(withdraw_order['account_id'], constant.SourceType.WITHDRAW, constant.WithdrawStep.SUCCESS,
                  withdraw_order['id'], withdraw_order['amount'])
    bookkeeping(event, '-frozen', '-asset')


@db_operate
def get_withdraw_order(db, order_id):
    return db.get("select * from withdraw where id=%(id)s", id=order_id)


@db_operate
def _get_frozen_withdraw_order(db, order_id, amount):
    return db.get("select * from withdraw where id=%(id)s and result=%(result)s and amount=%(amount)s",
                  id=order_id, result=constant.WithdrawResult.FROZEN, amount=amount)


@db_operate
def query_withdraw_order(db, account_id, order_id):
    return db.get("select * from withdraw where id=%(id)s and account_id=%(account_id)s",
                  id=order_id, account_id=account_id)


def is_successful_result(result):
    return result.upper() == 'SUCCESS'


def handle_withdraw_notify(order_id, data):
    try:
        with require_user_account_lock(order_id, 'cash') as _:
            # lock this order.
            amount = to_float(data['money_order'])
            withdraw_order = _get_frozen_withdraw_order(order_id, amount)
            if withdraw_order is None:
                notification.is_invalid()

            # dt_order = data['dt_order']
            paybill_id = data['oid_paybill']
            failure_info = data.get('info_order', '')
            result = data['result_pay']
            settle_date = data.get('settle_date', '')

            callback_url = withdraw_order['callback_url']
            if not is_successful_result(result):
                _fail_withdraw(withdraw_order, paybill_id, failure_info)
                notify_params = {'code': 0, 'account_id': withdraw_order['account_id'], 'order_id': order_id}
                _notify_client(callback_url, notify_params)
                return notification.fail()

            _succeed_withdraw(withdraw_order, paybill_id, settle_date)
            notify_params = {'code': 1, 'msg': 'failed', 'account_id': withdraw_order['account_id'], 'order_id': order_id}
            _notify_client(callback_url, notify_params)
            return notification.succeed()
    except GetLockError:
        return notification.is_invalid()
    except GetLockTimeoutError:
        return notification.is_invalid()


def _notify_client(url, params):
    req = requests.post(url, params)
    if req.status_code == 200:
        data = req.json()
        if data['code'] == 0:
            # success
            return
    # other notify process.
    # TODO
