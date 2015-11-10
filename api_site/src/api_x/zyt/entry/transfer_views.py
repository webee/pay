# coding=utf-8
from __future__ import unicode_literals
from api_x.utils import response
from api_x.zyt.biz import transfer
from api_x.zyt.biz.models import TransactionType
from api_x.zyt.user_mapping import get_user_domain_by_name

from flask import request
from . import biz_entry_mod as mod
from pytoolbox.util.log import get_logger
from api_x.utils.entry_auth import verify_request, prepay_entry


logger = get_logger(__name__)


@mod.route('/transfer', methods=['POST'])
@verify_request('transfer')
@prepay_entry(TransactionType.TRANSFER)
def transfer():
    data = request.values
    channel = request.channel
    from_user_domain_name = data['from_user_domain_name']
    from_user_id = data['from_user_id']
    to_user_domain_name = data['to_user_domain_name']
    to_user_id = data['to_user_id']
    order_id = data.get('order_id')
    amount = data['amount']
    info = data['info']

    try:
        tx = transfer.apply_to_transfer(channel, order_id,
                                        from_user_domain_name, from_user_id,
                                        to_user_domain_name, to_user_id, amount, info)
        return response.success(sn=tx.sn)
    except Exception as e:
        logger.exception(e)
        return response.fail(code=1, msg=e.message)

