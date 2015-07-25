# coding=utf-8
from datetime import datetime
from tools.dbe import db_operate


@db_operate
def set_refunded_amount(db, id, amount):
    return db.execute("""
                    UPDATE payment
                      SET refunded_amount=%(amount)s
                      WHERE id=%(id)s
    """, id=id, amount=amount) > 0


@db_operate
def transit_state(db, id, prev_state, new_state):
    return db.execute("""
                    UPDATE payment
                      SET state=%(new_state)s, updated=%(updated)s
                      WHERE id=%(id)s AND state=%(prev_state)s
        """, id=id, prev_state=prev_state, new_state=new_state, updated=datetime.now()) > 0
