# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import Blueprint, request
from api.core import transaction_log
from api.util import response

transaction_log_mod = Blueprint('transaction_log', __name__)
mod = transaction_log_mod


@mod.route('/accounts/<int:account_id>/cash_records', methods=['GET'])
def user_cash_records(account_id):
    page_no = int(request.args.get('page_no', 1))
    page_size = int(request.args.get('page_size', 20))
    cash_records, orders_info = transaction_log.get_user_cash_account_records(account_id, page_no, page_size)

    cash_records = [dict(cash_record) for cash_record in cash_records]
    orders_info = {order_id: dict(order) for order_id, order in orders_info.items()}

    return response.ok(records=cash_records, record_info=orders_info)
