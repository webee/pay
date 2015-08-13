# -*- coding: utf-8 -*-
from .balance import get_cash_balance, InsufficientBalanceError
from ._bookkeeping import bookkeep, Event, SourceType
from ._dba import find_bankcard_by_id, create_withdraw, transit_withdraw_state, WITHDRAW_STATE, \
    find_withdraw_by_id as _get_withdraw_by_id, update_withdraw_result, list_all_unfailed_withdraw, \
    find_withdraw_basic_info_by_id as _get_withdraw_basic_info_by_id, find_withdraw_by_id
from .ipay import transaction
from .util.lock import require_user_account_lock
from .util.handling_result import HandledResult
from api.core import ZytCoreError, ConditionalError
from api.util.notify import notify_client
from api.util.parser import to_int
from pytoolbox.util.dbe import db_transactional, transactional
from pytoolbox.util.log import get_logger


_logger = get_logger(__name__)


class BankcardNotFoundError(ConditionalError):
    def __init__(self, bankcard_id):
        message = "Cannot find bankcard with [bankcard_id={0}].".format(bankcard_id)
        super(BankcardNotFoundError, self).__init__(message)


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


def apply_to_withdraw(order_id, account_id, bankcard_id, amount, callback_url):
    bankcard = find_bankcard_by_id(to_int(bankcard_id))
    if bankcard is None:
        raise BankcardNotFoundError(bankcard_id)

    if amount <= 0:
        raise NegativeAmountError(amount)

    withdraw_id = _create_withdraw(order_id, account_id, bankcard.id, amount, callback_url)
    notify_url = transaction.generate_withdraw_notification_url(account_id, withdraw_id)
    _request_withdraw(withdraw_id, amount, bankcard, notify_url)

    return withdraw_id


def get_withdraw_by_id(withdraw_id):
    return _get_withdraw_by_id(withdraw_id)


def get_withdraw_basic_info_by_id(withdraw_id):
    return _get_withdraw_basic_info_by_id(withdraw_id)


@transactional
def handle_withdraw_notification(withdraw_id, paybill_id, result, failure_info=''):
    update_withdraw_result(withdraw_id, paybill_id, result, failure_info)
    _logger.warn("Withdraw notify result: [{0}], id=[{1}]".format(result, withdraw_id))

    if transaction.is_failed_withdraw(result):
        _fail_withdraw(withdraw_id)
        return HandledResult(True, False)
    elif transaction.is_successful_withdraw(result):
        _succeed_withdraw(withdraw_id)
        return HandledResult(True, True)

    return HandledResult(False)


def list_unfailed_withdraw(account_id):
    records = list_all_unfailed_withdraw(account_id)
    return [dict(record) for record in records]


def _create_withdraw(order_id, account_id, bankcard_id, amount, callback_url):
    with require_user_account_lock(account_id, 'cash'):
        balance = get_cash_balance(account_id)
        if amount > balance:
            raise InsufficientBalanceError()

        return _create_withdraw_to_be_frozen(order_id, account_id, bankcard_id, amount, callback_url)


@db_transactional
def _create_withdraw_to_be_frozen(db, trade_order_id, account_id, bankcard_id, amount, callback_url):
    withdraw_id = create_withdraw(db, trade_order_id, account_id, bankcard_id, amount, callback_url)
    _freeze_withdraw(db, withdraw_id, account_id, amount, bankcard_id)
    return withdraw_id


def _request_withdraw(withdraw_id, amount, bankcard, notify_url):
    order_info = u'自游通提现'
    try:
        transaction.pay_to_bankcard(withdraw_id, amount, order_info, bankcard, notify_url)
    except Exception, e:
        _fail_withdraw(withdraw_id)
        raise WithdrawRequestFailedError(withdraw_id, e.message)


@db_transactional
def _fail_withdraw(db, withdraw_id):
    withdraw_record = get_withdraw_by_id(withdraw_id)
    _unfreeze_withdraw_back_to_cash_account(db, withdraw_id, withdraw_record['account_id'], withdraw_record['amount'],
                                            withdraw_record['bankcard_id'])
    transit_withdraw_state(db, withdraw_id, WITHDRAW_STATE.FROZEN, WITHDRAW_STATE.FAILED)


@db_transactional
def _succeed_withdraw(db, withdraw_id):
    withdraw_record = get_withdraw_by_id(withdraw_id)
    _unfreeze_withdraw_to_bankcard(db, withdraw_id, withdraw_record['account_id'], withdraw_record['amount'],
                                   withdraw_record['bankcard_id'])
    transit_withdraw_state(db, withdraw_id, WITHDRAW_STATE.FROZEN, WITHDRAW_STATE.SUCCESS)


def _freeze_withdraw(db, withdraw_id, account_id, amount, bankcard_id):
    bookkeep(db,
             Event(SourceType.WITHDRAW_FROZEN, withdraw_id, amount, _generate_withdraw_info(bankcard_id)),
             (account_id, '-cash'),
             (account_id, '+frozen'))


def _unfreeze_withdraw_back_to_cash_account(db, withdraw_id, account_id, amount, bankcard_id):
    bookkeep(db,
             Event(SourceType.WITHDRAW_FAILED, withdraw_id, amount, _generate_withdraw_info(bankcard_id)),
             (account_id, '-frozen'),
             (account_id, '+cash'))


def _unfreeze_withdraw_to_bankcard(db, withdraw_id, account_id, amount, bankcard_id):
    bookkeep(db,
             Event(SourceType.WITHDRAW_SUCCESS, withdraw_id, amount, _generate_withdraw_info(bankcard_id)),
             (account_id, '-frozen'),
             (account_id, '-asset'))


def _generate_withdraw_info(bankcard_id):
    bankcard = find_bankcard_by_id(bankcard_id)
    bank_name = bankcard['bank_name']
    secured_card_no = _mask_bankcard_no(bankcard['card_no'])
    return u'提现至 {0}[{1}]'.format(bank_name, secured_card_no)


def _mask_bankcard_no(bankcard_no):
    return '{0} **** **** {1}'.format(bankcard_no[:4], bankcard_no[-4:])


def try_to_notify_withdraw_result_client(withdraw_order):
    withdraw_id = withdraw_order['id']
    url = withdraw_order['async_callback_url']
    amount = withdraw_order.amount
    account_id = withdraw_order.account_id

    if withdraw_order.state == WITHDRAW_STATE.SUCCESS:
        params = {'code': 0, 'account_id': account_id, 'order_id': withdraw_id, 'amount': amount}
    else:
        params = {'code': 1, 'msg': 'failed', 'account_id': account_id, 'order_id': withdraw_id, 'amount': amount}

    if not notify_client(url, params):
        from api.task import tasks
        tasks.withdraw_notify.delay(url, params)