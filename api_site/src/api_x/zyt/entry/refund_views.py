# coding=utf-8
from __future__ import unicode_literals

from flask import request
from . import entry_mod as mod
from api_x.util import response
from api_x.zyt.biz import refund


@mod.route('/refund', methods=['POST'])
def apply_to_refund():
    data = request.values
    channel_id = data['channel_id']
    order_id = data['order_id']
    amount = data['amount']
    client_notify_url = data['notify_url']

    refund_record = refund.apply_to_refund(channel_id, order_id, amount, client_notify_url)
    return response.accepted(refund_record.sn)
