# coding=utf-8
from datetime import datetime
from api.constant import WithdrawState
from api.util import oid
from tools.dbe import db_context


@db_context
def get_withdraw(db, withdraw_id):
    return db.get("select * from withdraw where id=%(id)s", id=withdraw_id)


@db_context
def get_account_withdraw(db, account_id, withdraw_id):
    return db.get("select * from withdraw where account_id=%(account_id)s and id=%(id)s",
                  account_id=account_id, id=withdraw_id)


@db_context
def transit_state(db, id, pre_state, new_state):
    return db.execute("""
            UPDATE withdraw
              SET state=%(new_state)s, updated_on=%(updated_on)s
              WHERE id=%(id)s and state=%(pre_state)s
    """, id=id, pre_state=pre_state, new_state=new_state, updated_on=datetime.now()) > 0


@db_context
def set_withdraw_info(db, refund_id, paybill_id, result, failure_info):
    return db.execute("""
            UPDATE withdraw
                SET paybill_id=%(paybill_id)s, result=%(result)s, failure_info=%(failure_info)s, updated_on=%(updated_on)s
                WHERE id=%(id)s AND state=%(state)s
        """, id=refund_id, state=WithdrawState.FROZEN, result=result,
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


@db_context
def list_all_withdraw(db, account_id):
    return db.list(_sql_to_query_withdraw() + 'AND withdraw.account_id = %(account_id)s', account_id=account_id)


@db_context
def find_withdraw_by_id(db, id):
    return db.get(_sql_to_query_withdraw() + 'AND withdraw.id = %(withdraw_id)s', withdraw_id=id)


def _sql_to_query_withdraw():
    return """
        SELECT withdraw.id,
               concat(bank_name, '(', right(card_no, 4), ')') AS card,
               withdraw.created_on AS withdrawed_on,
               if(withdraw.state = 'SUCCESS', withdraw.updated_on, null) AS received_on
        FROM withdraw
          INNER JOIN bankcard ON withdraw.bankcard_id = bankcard.id
        WHERE withdraw.state <> 'FAILED'
    """