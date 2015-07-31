# coding=utf-8
from datetime import datetime
from tools.dbe import db_context


@db_context
def set_refunded_amount(db, id, amount):
    return db.execute("""
                    UPDATE payment
                      SET refunded_amount=%(amount)s
                      WHERE id=%(id)s
    """, id=id, amount=amount) > 0


@db_context
def transit_state(db, id, prev_state, new_state):
    return db.execute("""
                    UPDATE payment
                      SET state=%(new_state)s, updated_on=%(updated_on)s
                      WHERE id=%(id)s AND state=%(prev_state)s
        """, id=id, prev_state=prev_state, new_state=new_state, updated_on=datetime.now()) > 0
