# coding=utf-8
from datetime import datetime
from api.constant import WithdrawState
from api.util import oid
from tools.dbe import db_operate


@db_operate
def get_withdraw(db, withdraw_id):
    return db.get("select * from withdraw where id=%(id)s", id=withdraw_id)


@db_operate
def get_account_withdraw(db, account_id, withdraw_id):
    return db.get("select * from withdraw where account_id=%(account_id)s and id=%(id)s",
                  account_id=account_id, id=withdraw_id)


@db_operate
def transit_state(db, id, pre_state, new_state):
    return db.execute("""
            UPDATE withdraw
              SET state=%(new_state)s, updated_on=%(updated_on)s
              WHERE id=%(id)s and state=%(pre_state)s
    """, id=id, pre_state=pre_state, new_state=new_state, updated_on=datetime.now()) > 0


@db_operate
def set_withdraw_info(db, refund_id, paybill_id, failure_info):
    return db.execute("""
            UPDATE withdraw
                SET paybill_id=%(paybill_id)s, failure_info=%(failure_info)s, updated_on=%(updated_on)s
                WHERE id=%(id)s AND state=%(state)s
        """, id=refund_id, state=WithdrawState.FROZEN,
                      paybill_id=paybill_id, failure_info=failure_info, updated_on=datetime.now()) > 0


def create_withdraw(db, account_id, bankcard_id, amount, callback_url):
    order_id = oid.withdraw_id(account_id)
    fields = {
        'id': order_id,
        'account_id': account_id,
        'bankcard_id': bankcard_id,
        'amount': amount,
        'created_on': datetime.now(),
        'callback_url': callback_url,
        'state': WithdrawState.FROZEN
    }

    db.insert('withdraw', fields)

    return order_id
