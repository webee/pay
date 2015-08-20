# coding=utf-8
from __future__ import unicode_literals
from api_x import db
from api_x.constant import WithdrawTransactionState
from api_x.dbs import transactional, require_transaction_context
from api_x.zyt.biz.commons import is_duplicated_notify
from api_x.zyt.biz.models import TransactionType, WithdrawRecord
from api_x.zyt.biz.transaction import create_transaction, transit_transaction_state, get_tx_by_id
from api_x.zyt.biz.withdraw.dba import get_tx_withdraw_by_sn
from api_x.zyt.biz.withdraw.error import WithdrawFailedError
from api_x.zyt.vas.user import get_user_cash_balance
from api_x.zyt.vas.models import EventType
from api_x.zyt.vas.bookkeep import bookkeeping
from api_x.zyt.vas import NAME as ZYT_NAME
from api_x.zyt.biz.transaction import update_transaction_info
from api_x.zyt.biz.error import *
from tools.mylog import get_logger


logger = get_logger(__name__)


def apply_to_withdraw(from_user_id,
                      flag_card, card_type, card_no, acct_name, bank_code, province_code,
                      city_code, bank_name, brabank_name, prcptcd,
                      amount, fee, client_notify_url, data):
    if amount <= 0:
        raise NonPositiveAmountError(amount)
    if fee < 0:
        raise AmountValueError('fee must be non-negative value.')

    withdraw_record = _create_and_request_withdraw(from_user_id,
                                                   flag_card, card_type, card_no, acct_name, bank_code, province_code,
                                                   city_code, bank_name, brabank_name, prcptcd,
                                                   amount, fee, client_notify_url, data)
    return withdraw_record


@transactional
def _create_and_request_withdraw(from_user_id,
                                 flag_card, card_type, card_no, acct_name, bank_code, province_code,
                                 city_code, bank_name, brabank_name, prcptcd,
                                 amount, fee, client_notify_url, data):
    tx, withdraw_record = _create_withdraw(from_user_id,
                                           flag_card, card_type, card_no, acct_name, bank_code, province_code,
                                           city_code, bank_name, brabank_name, prcptcd,
                                           amount, fee, client_notify_url, data)
    try:
        _request_pay_to_bankcard(tx, withdraw_record, data)
        _withdraw_to_processing(tx)
    except Exception as e:
        logger.exception(e)
        # FIXME: because this is in a transaction, below is useless.
        _unfreeze_fail_withdraw(tx, withdraw_record)
        raise e

    return withdraw_record


@transactional
def _create_withdraw(from_user_id,
                     flag_card, card_type, card_no, acct_name, bank_code, province_code,
                     city_code, bank_name, brabank_name, prcptcd,
                     amount, fee, client_notify_url, data):
    # 计算相关金额
    balance = get_user_cash_balance(from_user_id)
    ac = balance.available
    if ac <= fee or amount > ac:
        # 余额不足
        raise InsufficientAvailableBalanceError()

    if amount <= ac - fee:
        actual_amount = amount
    else:
        actual_amount = ac - fee

    comments = "提现至 {0}({1}) {2}".format(bank_name, card_no[-4:], acct_name)
    tx = create_transaction(TransactionType.WITHDRAW, actual_amount + fee, comments, [from_user_id])

    fields = {
        'tx_id': tx.id,
        'sn': tx.sn,
        'from_user_id': from_user_id,
        'flag_card': flag_card,
        'card_type': card_type,
        'card_no': card_no,
        'acct_name': acct_name,
        'bank_code': bank_code,
        'province_code': province_code,
        'city_code': city_code,
        'bank_name': bank_name,
        'brabank_name': brabank_name,
        'prcptcd': prcptcd,
        'amount': amount,
        'actual_amount': actual_amount,
        'fee': fee,
        'client_notify_url': client_notify_url
    }

    withdraw_record = WithdrawRecord(**fields)
    db.session.add(withdraw_record)

    _freeze_withdraw(tx, withdraw_record)

    return tx, withdraw_record


@transactional
def _freeze_withdraw(tx, withdraw_record):
    from_user_id = withdraw_record.from_user_id
    fee = withdraw_record.fee
    actual_amount = withdraw_record.actual_amount

    event_ids = []
    # 冻结相关资金
    if fee > 0:
        # 手续费
        event_id = bookkeeping(EventType.FREEZE, tx.sn, from_user_id, ZYT_NAME, fee)
        event_ids.append(event_id)
    # 提现金额
    event_id = bookkeeping(EventType.FREEZE, tx.sn, from_user_id, ZYT_NAME, actual_amount)
    event_ids.append(event_id)

    transit_transaction_state(tx.id, WithdrawTransactionState.CREATED, WithdrawTransactionState.FROZEN, event_ids)


@transactional
def _unfreeze_fail_withdraw(tx, withdraw_record):
    event_ids = _unfreeze_withdraw_amount(tx, withdraw_record)
    transit_transaction_state(tx.id, WithdrawTransactionState.FROZEN, WithdrawTransactionState.FAILED, event_ids)


@transactional
def _fail_withdraw(tx, withdraw_record):
    event_ids = _unfreeze_withdraw_amount(tx, withdraw_record)
    transit_transaction_state(tx.id, WithdrawTransactionState.PROCESSING, WithdrawTransactionState.FAILED, event_ids)


def _unfreeze_withdraw_amount(tx, withdraw_record):
    from_user_id = withdraw_record.from_user_id
    fee = withdraw_record.fee
    actual_amount = withdraw_record.actual_amount

    event_ids = []
    # 冻结相关资金
    if fee > 0:
        # 手续费
        event_id = bookkeeping(EventType.UNFREEZE, tx.sn, from_user_id, ZYT_NAME, fee)
        event_ids.append(event_id)
    # 提现金额
    event_id = bookkeeping(EventType.UNFREEZE, tx.sn, from_user_id, ZYT_NAME, actual_amount)
    event_ids.append(event_id)

    return event_ids


@transactional
def _success_withdraw(tx, withdraw_record):
    from_user_id = withdraw_record.from_user_id
    fee = withdraw_record.fee
    actual_amount = withdraw_record.actual_amount

    event_ids = []
    if fee > 0:
        from api_x.zyt.vas.pattern import transfer_frozen
        from api_x.zyt.user_mapping import get_lvye_corp_account_user_id
        from api_x.constant import LVYE_CORP_USER_NAME
        lvye_corp_user_id = get_lvye_corp_account_user_id(LVYE_CORP_USER_NAME)
        # 手续费转账
        event_ids.extend(transfer_frozen(tx.sn, from_user_id, lvye_corp_user_id, fee))
    # 提现金额转出
    event_id = bookkeeping(EventType.TRANSFER_OUT_FROZEN, tx.sn, from_user_id, ZYT_NAME, actual_amount)
    event_ids.append(event_id)

    transit_transaction_state(tx.id, WithdrawTransactionState.PROCESSING, WithdrawTransactionState.SUCCESS, event_ids)


@transactional
def _withdraw_to_processing(tx):
    transit_transaction_state(tx.id, WithdrawTransactionState.FROZEN, WithdrawTransactionState.PROCESSING)


def _request_pay_to_bankcard(tx, withdraw_record, data):
    if 'use_test_pay' in data and data['use_test_pay'] == '1':
        # for test.
        return _withdraw_by_test_pay(tx, withdraw_record, data)
    else:
        return _withdraw_by_lianlian_pay(tx, withdraw_record)


def _withdraw_by_test_pay(tx, withdraw_record, data):
    """test_pay代付"""
    from api_x.zyt.evas.test_pay import pay_to_bankcard
    from api_x.zyt.evas.test_pay.commons import is_success_request

    result = data.get('result')
    res = pay_to_bankcard(TransactionType.WITHDRAW, tx.sn, withdraw_record.actual_amount, result or 'SUCCESS')

    if not is_success_request(res):
        raise WithdrawFailedError(res['reg_msg'])
    return res


def _withdraw_by_lianlian_pay(tx, withdraw_record):
    """连连代付"""
    from api_x.zyt.evas.lianlian_pay import pay_to_bankcard
    from api_x.zyt.evas.lianlian_pay.commons import is_success_request

    res = pay_to_bankcard(TransactionType.WITHDRAW, tx.sn, withdraw_record.actual_amount, '提现到银行卡',
                          withdraw_record.flag_card, withdraw_record.card_type, withdraw_record.card_no,
                          withdraw_record.acct_name, withdraw_record.bank_code, withdraw_record.province_code,
                          withdraw_record.city_code, withdraw_record.brabank_name, withdraw_record.prcptcd)

    if not is_success_request(res):
        raise WithdrawFailedError(res['ret_msg'])
    return res


def handle_withdraw_notify(is_success, sn, vas_name, vas_sn, data):
    tx, withdraw_record = get_tx_withdraw_by_sn(sn)

    logger.info('withdraw notify: {0}'.format(data))
    if tx is None or withdraw_record is None:
        # 不存在
        logger.warning('withdraw [{0}] not exits.'.format(sn))
        return

    if is_duplicated_notify(tx, vas_name, vas_sn):
        logger.warning('withdraw notify duplicated: [{0}, {1}]'.format(vas_name, vas_sn))
        return

    if tx.state != WithdrawTransactionState.PROCESSING:
        logger.warning('bad withdraw notify: [sn: {0}]'.format(sn))
        return

    _record_withdraw_extra_info(withdraw_record, data)
    with require_transaction_context():
        tx = update_transaction_info(tx.id, vas_name, vas_sn)
        if is_success:
            _success_withdraw(tx, withdraw_record)
        else:
            _fail_withdraw(tx, withdraw_record)

    # notify client.
    tx = get_tx_by_id(tx.id)
    _try_notify_client(tx, withdraw_record)


def _try_notify_client(tx, withdraw_record):
    from api_x.utils.notify import notify_client
    url = withdraw_record.client_notify_url

    if tx.state == WithdrawTransactionState.SUCCESS:
        params = {'code': 0, 'account_user_id': withdraw_record.from_user_id, 'sn': tx.sn,
                  'amount': withdraw_record.amount, 'actual_amount': withdraw_record.actual_amount,
                  'fee': withdraw_record.fee}
    elif tx.state == WithdrawTransactionState.FAILED:
        params = {'code': 1, 'account_user_id': withdraw_record.from_user_id, 'sn': tx.sn,
                  'amount': withdraw_record.amount, 'actual_amount': withdraw_record.actual_amount,
                  'fee': withdraw_record.fee}

    if not notify_client(url, params):
        # other notify process.
        from api_x.task import tasks
        tasks.withdraw_notify.delay(url, params)


def _record_withdraw_extra_info(withdraw_record, data):
    pass
