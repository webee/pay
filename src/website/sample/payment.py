# -*- coding: utf-8 -*-
from tools.dbe import from_db


def find_by_orderno(order_no):
    return from_db().get('SELECT * FROM payment WHERE client_id = 1 AND order_id = %(order_id)s', order_id=order_no)
