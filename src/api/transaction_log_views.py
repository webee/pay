# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import Blueprint
from api.core import transaction_log
from api.util import response

transaction_log_mod = Blueprint('transaction_log', __name__)
mod = transaction_log_mod


@mod.route('/accounts/<int:account_id>/cash_records', methods=['GET'])
def user_cash_records(account_id):
    cash_records = transaction_log.get_user_cash_account_records(account_id)

    cash_records = [dict(cash_record) for cash_record in cash_records]

    return response.list_data(cash_records)
