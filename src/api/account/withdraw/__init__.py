# coding=utf-8
from __future__ import unicode_literals
from decimal import Decimal, InvalidOperation

from api.account.withdraw import notify
from api.commons.error import *
from api.account.error import *
from api.util.ipay import transaction
from api.util.ipay.error import ApiError
from api.account.withdraw.error import WithdrawError, WithdrawRequestFailedError
from tools.dbe import db_transactional, transactional
from api.constant import WithdrawState
from tools.utils import to_int
from ..bankcard import get_bankcard
from tools.lock import require_user_account_lock, GetLockError, GetLockTimeoutError
from api.util.ipay.transaction import notification
from . import dba, transit
from .. import account
from tools.mylog import get_logger
from top_config import lianlian

logger = get_logger(__name__)


def apply_for_withdraw(account_id, bankcard_id, amount, callback_url):
    bankcard = get_bankcard(account_id, to_int(bankcard_id))
    if bankcard is None:
        raise NoBankcardFoundError(account_id, bankcard_id)

    try:
        amount_value = Decimal(amount)
    except InvalidOperation:
        raise AmountValueError(amount)

    if amount_value <= 0:
        raise AmountNotPositiveError(amount_value)

    withdraw_id = _create_withdraw_freezing(account_id, bankcard.id, amount_value, callback_url)
    _request_withdraw(withdraw_id, amount, bankcard)

    return withdraw_id


def handle_withdraw_notify(withdraw_id, data):
    amount = Decimal(data['money_order'])
    withdraw_order = dba.get_withdraw(withdraw_id)
    if withdraw_order is None:
        return notification.is_invalid()
    elif withdraw_order.state != WithdrawState.FROZEN:
        return notification.duplicate()
    elif withdraw_order.amount != amount:
        return notification.is_invalid()

    paybill_id = data['oid_paybill']
    failure_info = data.get('info_order', '')
    result = data['result_pay']
    if _process_withdraw_result(withdraw_id, paybill_id, result, failure_info):
        notify.try_notify_client(withdraw_id)
        return notification.accepted()
    return notification.refused()


def query_order_to_update_state(account_id, withdraw_id):
    withdraw_order = dba.get_account_withdraw(account_id, withdraw_id)
    if withdraw_order is None or withdraw_order.state != WithdrawState.FROZEN:
        return withdraw_order

    try:
        data = transaction.query_withdraw_order(withdraw_id)
    except ApiError:
        return withdraw_order

    paybill_id = data['oid_paybill']
    failure_info = data.get('info_order', '')
    result = data['result_pay']
    if _process_withdraw_result(withdraw_id, paybill_id, result, failure_info):
        notify.try_notify_client(withdraw_id)
        return dba.get_withdraw(withdraw_id)
    return withdraw_order


@db_transactional
def _create_withdraw_freezing(db, account_id, bankcard_id, amount, callback_url):
    try:
        with require_user_account_lock(account_id, 'cash') as _:
            balance = account.get_cash_balance(account_id)
            if amount > balance:
                raise InsufficientBalanceError()
            withdraw_id = dba.create_withdraw(db, account_id, bankcard_id, amount, callback_url)
            transit.withdraw_frozen(withdraw_id)

            return withdraw_id
    except GetLockError as e:
        raise WithdrawError(e.message)
    except GetLockTimeoutError as e:
        raise WithdrawError(e.message)


def _request_withdraw(withdraw_id, amount, bankcard):
    order_info = "自游通提现"
    try:
        _ = transaction.pay_to_bankcard(withdraw_id, amount, order_info, bankcard)
    except ApiError:
        _process_request_failed(withdraw_id)
        raise WithdrawRequestFailedError(withdraw_id)


@transactional
def _process_request_failed(withdraw_id):
    transit.withdraw_failed(withdraw_id)


@transactional
def _process_withdraw_result(withdraw_id, paybill_id, result, failure_info):
    if dba.set_withdraw_info(withdraw_id, paybill_id, failure_info):
        # process withdraw result.
        if result == lianlian.PayToBankcard.Result.FAILURE:
            transit.withdraw_failed(withdraw_id)
        elif result == lianlian.PayToBankcard.Result.SUCCESS:
            transit.withdraw_success(withdraw_id)
        else:
            logger.warn("withdraw notify result: [{0}], id=[{1}]".format(result, withdraw_id))
            return False
        return True
