# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import Blueprint, request
from api.core import transaction_log
from api.util import response

transaction_log_mod = Blueprint('transaction_log', __name__)
mod = transaction_log_mod


@mod.route('/accounts/<int:account_id>/cash_records', methods=['GET'])
def user_cash_records(account_id):
    q = request.args.get('q', '')
    side = request.args.get('side', '')
    tp = request.args.get('tp', '')
    page_no = int(request.args.get('page_no', 1))
    page_size = int(request.args.get('page_size', 20))
    count, cash_records, orders_info = transaction_log.get_user_cash_account_records(account_id, q, side, tp, page_no, page_size)

    cash_records = [dict(cash_record) for cash_record in cash_records]
    orders_info = {order_id: dict(order) for order_id, order in orders_info.items()}

    return response.ok(count=count, page_no=page_no, page_size=page_size,
                       records=cash_records, record_infos=orders_info)
