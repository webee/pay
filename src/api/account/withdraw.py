# coding=utf-8
from __future__ import unicode_literals
from datetime import datetime

from tools.dbi import from_db, transactional, require_transaction_context
from api.util import id
from api import constant
from api.util.bookkeeping import bookkeeping, Event
from tools.mylog import get_logger


logger = get_logger(__name__)


def create_withdraw_order_and_freeze_cash(account_id, bankcard_id, amount, callback_url):
    """ 新建提现订单并冻结金额
    :param account_id: 提现账户id
    :param bankcard_id: 银行卡id
    :param amount: 提现金额
    :param callback_url: 请求方回调通知url
    :return:
    """
    order_id = None
    try:
        with require_transaction_context():
            order_id = create_withdraw_order(account_id, bankcard_id, amount, callback_url)
            freeze_withdraw_cash(account_id, order_id, amount)
    except Exception as e:
        logger.warn('create withdraw order failed: %s, %s, %s, %s, %s',
                    account_id, bankcard_id, amount, callback_url, e.message)

    return order_id


def create_withdraw_order(account_id, bankcard_id, amount, callback_url):
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

    from_db().insert('withdraw', **fields)

    return order_id


def freeze_withdraw_cash(account_id, source_id, amount):
    event = Event(account_id, constant.SourceType.WITHDRAW, constant.WithdrawStep.FROZEN, source_id, amount),
    bookkeeping(event, '+frozen', '-cash')


def unfreeze_back_withdraw_cash(account_id, source_id, amount):
    event = Event(account_id, constant.SourceType.WITHDRAW, constant.WithdrawStep.FAILED, source_id, amount),
    bookkeeping(event, '+cash', '-frozen')


def unfreeze_out_withdraw_cash(account_id, source_id, amount):
    event = Event(account_id, constant.SourceType.WITHDRAW, constant.WithdrawStep.SUCCESS, source_id, amount),
    bookkeeping(event, '-frozen', '-asset')


def get_withdraw_order(order_id):
    db = from_db()
    return db.get("select * from withdraw where id=%(id)s", id=order_id)


@transactional
def withdraw_request_failed(order_id):
    withdraw_order = get_withdraw_order(order_id)
    if withdraw_order:
        db = from_db()
        db.execute("update withdraw set result=%(result)s, failure_info=%(failure_info)s, ended_on=%(ended_on)s"
                   "where id=%(id)s", result=constant.WithdrawResult.FAILED,
                   failure_info='withdraw request failed.', ended_on=datetime.now(), id=order_id)

        unfreeze_back_withdraw_cash(withdraw_order['account_id'], order_id, withdraw_order['amount'])


@transactional
def withdraw_order_end(withdraw_order, paybill_id, result, failure_info, settle_date):
    db = from_db()
    db.execute("update withdraw set paybill_id=%(paybill_id)s, result=%(result)s,"
               "failure_info=%(failure_info)s, settle_date=%()s, ended_on=%(ended_on)s "
               "where id=%(id)s", paybill_id=paybill_id, result=result, failure_info=failure_info,
               settle_date=settle_date, ended_on=datetime.now(), id=withdraw_order['order_id'])
    unfreeze_out_withdraw_cash(withdraw_order['account_id'], withdraw_order['order_id'], withdraw_order['amount'])
