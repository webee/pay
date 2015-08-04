# -*- coding: utf-8 -*-
from decimal import Decimal, InvalidOperation

from .balance import get_cash_balance
from .bookkeeping import bookkeep, Event, SourceType
from .dba import find_bankcard_by_id, create_withdraw, transit_withdraw_state, WITHDRAW_STATE, \
    find_withdraw_by_id as _get_withdraw_by_id, update_withdraw_result, list_all_unfailed_withdraw, \
    find_withdraw_basic_info_by_id as _get_withdraw_basic_info_by_id
from .ipay import transaction
from .ipay.error import TransactionApiError
from .util.lock import require_user_account_lock
from .util.notify import try_to_notify_client
from api2.core import ZytCoreError, ConditionalError
from api2.util.parser import to_int
from pytoolbox import config
from pytoolbox.util.dbe import transactional
from pytoolbox.util.log import get_logger

_logger = get_logger(__name__)

_PAY_TO_BANKCARD_RESULT_SUCCESS = config.get('lianlianpay', 'pay_to_bankcard_result_success')
_PAY_TO_BANKCARD_RESULT_FAILURE = config.get('lianlianpay', 'pay_to_bankcard_result_failure')


class BankcardNotFoundError(ConditionalError):
    def __init__(self, bankcard_id):
        message = "Cannot find bankcard with [bankcard_id={0}].".format(bankcard_id)
        super(BankcardNotFoundError, self).__init__(message)


class InsufficientBalanceError(ConditionalError):
    def __init__(self):
        message = "Insufficient balance error."
        super(InsufficientBalanceError, self).__init__(message)


class AmountValueError(ConditionalError):
    def __init__(self, amount):
        message = "Amount value error: [{0}]".format(amount)
        super(AmountValueError, self).__init__(message)


class NegativeAmountError(ConditionalError):
    def __init__(self, amount):
        message = "Amount must be positive: [{0}]".format(amount)
        super(NegativeAmountError, self).__init__(message)


class WithdrawRequestFailedError(ZytCoreError):
    def __init__(self, withdraw_id, msg):
        message = "request withdraw failed: [{0}] [{1}].".format(withdraw_id, msg)
        super(WithdrawRequestFailedError, self).__init__(message)
        self.withdraw_id = withdraw_id


def apply_to_withdraw(account_id, bankcard_id, amount, callback_url):
    bankcard = find_bankcard_by_id(to_int(bankcard_id))
    if bankcard is None:
        raise BankcardNotFoundError(bankcard_id)

    try:
        amount_value = Decimal(amount)
    except InvalidOperation:
        raise AmountValueError(amount)

    if amount_value <= 0:
        raise NegativeAmountError(amount_value)

    withdraw_id = _create_withdraw_freezing(account_id, bankcard.id, amount_value, callback_url)
    notify_url = transaction.generate_withdraw_notification_url(account_id, withdraw_id)
    _request_withdraw(withdraw_id, amount, bankcard, notify_url)

    return withdraw_id


def get_withdraw_by_id(withdraw_id):
    return _get_withdraw_by_id(withdraw_id)


def get_withdraw_basic_info_by_id(withdraw_id):
    return _get_withdraw_basic_info_by_id(withdraw_id)


def handle_withdraw_notification(withdraw_id, paybill_id, result, failure_info=''):
    if _process_withdraw_result(withdraw_id, paybill_id, result, failure_info):
        try_to_notify_client(withdraw_id)
        return True
    return False


def list_unfailed_withdraw(account_id):
    records = list_all_unfailed_withdraw(account_id)
    return [dict(record) for record in records]


@transactional
def _create_withdraw_freezing(db, account_id, bankcard_id, amount, callback_url):
    with require_user_account_lock(account_id, 'cash'):
        balance = get_cash_balance(account_id)
        if amount > balance:
            raise InsufficientBalanceError()

        withdraw_id = create_withdraw(db, account_id, bankcard_id, amount, callback_url)
        _freeze_withdraw(db, withdraw_id, account_id, amount)
        return withdraw_id


def _request_withdraw(withdraw_id, amount, bankcard, notify_url):
    order_info = '自游通提现'
    try:
        transaction.pay_to_bankcard(withdraw_id, amount, order_info, bankcard, notify_url)
    except TransactionApiError, e:
        _fail_withdraw(withdraw_id)
        raise WithdrawRequestFailedError(withdraw_id, e.message)


@transactional
def _fail_withdraw(db, withdraw_id):
    withdraw_record = get_withdraw_by_id(withdraw_id)
    _unfreeze_withdraw(db, withdraw_id, withdraw_record['account_id'], withdraw_record['amount'])
    transit_withdraw_state(db, withdraw_id, WITHDRAW_STATE.FROZEN, WITHDRAW_STATE.SUCCESS)


def _freeze_withdraw(db, withdraw_id, account_id, amount):
    bookkeep(db,
             Event(SourceType.WITHDRAW_FROZEN, withdraw_id, amount),
             (account_id, '-cash'),
             (account_id, '+frozen'))


def _unfreeze_withdraw(db, withdraw_id, account_id, amount):
    bookkeep(db,
             Event(SourceType.WITHDRAW_FAILED, withdraw_id, amount),
             (account_id, '-frozen'),
             (account_id, '+cash'))


@transactional
def _process_withdraw_result(db, withdraw_id, paybill_id, result, failure_info):
    update_withdraw_result(withdraw_id, paybill_id, result, failure_info)
    _logger.warn("Withdraw notify result: [{0}], id=[{1}]".format(result, withdraw_id))

    if result == _PAY_TO_BANKCARD_RESULT_FAILURE:
        transit_withdraw_state(db, withdraw_id, WITHDRAW_STATE.FROZEN, WITHDRAW_STATE.FAILED)
        return True

    if result == _PAY_TO_BANKCARD_RESULT_SUCCESS:
        transit_withdraw_state(db, withdraw_id, WITHDRAW_STATE.FROZEN, WITHDRAW_STATE.SUCCESS)
        return True

    return False
