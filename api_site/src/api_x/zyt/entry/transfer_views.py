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
    from_user_id = data['from_user_id']
    to_user_id = data['to_user_id']
    to_user_domain_name = data.get('to_user_domain_name')
    order_id = data.get('order_id')
    amount = data['amount']

    from_user_map = channel.get_user_map(from_user_id)
    if from_user_map is None:
        return response.fail(msg="from user with domain [{0}] user [{1}] not exists.".format(channel.user_domain.name, from_user_id))
    if not to_user_domain_name:
        # 默认from用户域和to是一致的
        to_user_map = channel.get_user_map(to_user_id)
        if to_user_map is None:
            return response.fail(msg="to user with domain [{0}] user [{1}] not exists.".format(channel.user_domain.name, to_user_id))
    else:
        # 指定不同的payee用户域
        to_user_domain = get_user_domain_by_name(to_user_domain_name)
        if to_user_domain is None:
            return response.fail(msg="domain [{0}] not exists.".format(to_user_domain_name))
        to_user_map = to_user_domain.get_user_map(to_user_id)
        if to_user_map is None:
            return response.fail(msg="to user with domain [{0}] user [{1}] not exists.".format(to_user_domain_name, to_user_id))

    try:
        tx = transfer.apply_to_transfer(channel, order_id, from_user_map.account_user_id,
                                        to_user_map.account_user_id, amount)
        return response.success(sn=tx.sn)
    except Exception as e:
        logger.exception(e)
        return response.fail(code=1, msg=e.message)

