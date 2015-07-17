# coding=utf-8
from __future__ import unicode_literals
from datetime import datetime

from tools.dbi import from_db, transactional
from api.util import id
from api import constant
from api.util.bookkeeping import two_accounts_bookkeeping


@transactional
def create_withdraw_order(account_id, bandcard_id, amount, callback_url):
    """ 新建提现订单
    :param account_id: 提现账户id
    :param bandcard_id: 银行卡id
    :param amount: 提现金额
    :param callback_url: 请求方回调通知url
    :return:
    """
    order_id = id.withdraw_id(account_id)
    fields = {
        'id': order_id,
        'account_id': account_id,
        'bankcard_id': bandcard_id,
        'amount': amount,
        'created_on': datetime.now(),
        'callback_url': callback_url
    }

    from_db().insert('withdraw', **fields)

    return order_id


def get_withdraw_order(order_id):
    db = from_db()
    return db.get("select * from withdraw where id=%(id)s", id=order_id)


@transactional
def withdraw_request_failed(order_id):
    db = from_db()
    db.execute("update withdraw set result=%(result)s, failure_info=%(failure_info)s, ended_on=%(ended_on)s"
               "where id=%(id)s", result=constant.withdraw.WITHDRAW_REQUEST_FAILED,
               failure_info='withdraw request failed.', ended_on=datetime.now(), id=order_id)


@transactional
def withdraw_order_end(order_id, paybill_id, result, failure_info, settle_date):
    db = from_db()
    db.execute("update withdraw set paybill_id=%(paybill_id)s, result=%(result)s,"
               "failure_info=%(failure_info)s, settle_date=%()s, ended_on=%(ended_on)s "
               "where id=%(id)s", paybill_id=paybill_id, result=result, failure_info=failure_info,
               settle_date=settle_date, ended_on=datetime.now(), id=order_id)


def freeze_withdraw_cash(account_id, source_id, amount):
    source_type = constant.source_type.WITHDRAW,
    debit_account = 'cash'
    credit_account = 'frozen'
    now = datetime.now()
    event = {
        'account_id': account_id,
        'source_type': source_type,
        'step': constant.STEP_FROZEN,
        'source_id': source_id,
        'amount': amount,
        'created_on': now
    }

    return two_accounts_bookkeeping(event, debit_account, credit_account)

