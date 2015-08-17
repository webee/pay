# coding=utf-8
from __future__ import unicode_literals

from flask import request
from . import entry_mod as mod
from api_x.util import response
from api_x.zyt.biz import refund
from tools.mylog import get_logger

logger = get_logger(__name__)


@mod.route('/refund', methods=['POST'])
def apply_to_refund():
    data = request.values
    channel_id = data['channel_id']
    order_id = data['order_id']
    amount = data['amount']
    client_notify_url = data['notify_url']

    try:
        refund_record = refund.apply_to_refund(channel_id, order_id, amount, client_notify_url)
        return response.success(sn=refund_record.sn)
    except Exception as e:
        logger.exception(e)
        return response.fail(code=1, msg=e.message)
