# coding=utf-8
from tools.dbe import db_operate
from api.constant import RefundState
from datetime import datetime
from api.util import oid


@db_operate
def transit_state(db, id, pre_state, new_state):
    return db.execute("""
            UPDATE refund
              SET state=%(new_state)s, updated_on=%(ended_on)s
              WHERE id=%(id)s and state=%(pre_state)s
    """, id=id, pre_state=pre_state, new_state=new_state, updated_on=datetime.now()) > 0


@db_operate
def create_refund(db, payment_id, payer_account_id, payee_account_id, amount, callback_url=None):
    refund_id = oid.refund_id(payer_account_id)
    fields = {
        'id': refund_id,
        'payment_id': payment_id,
        'payer_account_id': payer_account_id,
        'payee_account_id': payee_account_id,
        'amount': amount,
        'state': RefundState.FROZEN,
        'created_on': datetime.now(),
        'callback_url': callback_url
    }
    db.insert('refund', returns_id=True, **fields)
    return refund_id


@db_operate
def get_refund(db, id):
    return db.get('SELECT * FROM refund WHERE id=%(id)s', id=id)


@db_operate
def get_payment(db, client_id, order_id):
    return db.get("""
            SELECT *
              FROM payment
              WHERE client_id = %(client_id)s AND order_id = %(order_id)s
        """, client_id=client_id, order_id=order_id)


@db_operate
def set_refund_info(db, refund_id, refund_serial_no):
    return db.execute("""
            UPDATE refund
                SET refund_serial_no=%(refund_serial_no)s, updated_on=%(updated_on)
                WHERE id=%(id)s
        """, id=refund_id, refund_serial_no=refund_serial_no, updated_on=datetime.now()) > 0
