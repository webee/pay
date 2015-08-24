# coding=utf-8
from __future__ import unicode_literals
from api_x.utils import response

from flask import request
from . import biz_entry_mod as mod
from api_x.zyt.biz import refund
from api_x.utils.entry_auth import verify_request
from pytoolbox.util.log import get_logger

logger = get_logger(__name__)


@mod.route('/refund', methods=['POST'])
@verify_request('refund')
def apply_to_refund():
    data = request.values
    channel = request.channel
    order_id = data['order_id']
    amount = data['amount']
    client_notify_url = data['notify_url']

    logger.info('receive refund: {0}'.format({k: v for k, v in data.items()}))
    try:
        refund_record = refund.apply_to_refund(channel, order_id, amount, client_notify_url, data)
        return response.success(sn=refund_record.sn)
    except Exception as e:
        logger.exception(e)
        return response.fail(code=1, msg=e.message)
