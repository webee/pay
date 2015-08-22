# coding=utf-8
from __future__ import unicode_literals
from api_x.utils import response
from api_x.zyt.user_mapping import get_channel_by_name

from flask import request
from . import biz_entry_mod as mod
from api_x.zyt.biz import refund
from pytoolbox.util.log import get_logger

logger = get_logger(__name__)


@mod.route('/refund', methods=['POST'])
def apply_to_refund():
    data = request.values
    channel_name = data['channel_name']
    order_id = data['order_id']
    amount = data['amount']
    client_notify_url = data['notify_url']

    logger.info('receive refund: {0}'.format({k: v for k, v in data.items()}))
    channel = get_channel_by_name(channel_name)
    if channel is None:
        return response.fail(msg='channel not exits: [{0}]'.format(channel_name))

    try:
        refund_record = refund.apply_to_refund(channel, order_id, amount, client_notify_url, data)
        return response.success(sn=refund_record.sn)
    except Exception as e:
        logger.exception(e)
        return response.fail(code=1, msg=e.message)
