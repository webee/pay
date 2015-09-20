# coding=utf-8
from __future__ import unicode_literals
from api_x.utils import response
from api_x.zyt.biz.prepaid import create_prepaid
from api_x.zyt.user_mapping import get_user_domain_by_name

from flask import request
from . import biz_entry_mod as mod
from pytoolbox.util.log import get_logger
from api_x.utils.entry_auth import verify_request


logger = get_logger(__name__)


@mod.route('/preprepaid', methods=['POST'])
@verify_request('preprepaid')
def preprepaid():
    data = request.values
    channel = request.channel
    order_id = data.get('order_id')
    to_user_id = data['to_user_id']
    to_domain_name = data.get('to_domain_name')
    amount = data['amount']
    client_callback_url = data['callback_url']
    client_notify_url = data['notify_url']

    if not to_domain_name:
        to_user_map = channel.get_user_map(to_user_id)
    else:
        # 指定不同的to用户域
        to_domain = get_user_domain_by_name(to_domain_name)
        if to_domain is None:
            return response.fail(msg="domain [{0}] not exists.".format(to_domain_name))
        to_user_map = to_domain.get_user_map(to_user_id)
        if to_user_map is None:
            return response.fail(msg="to with domain [{0}] user [{1}] not exists.".format(to_domain_name,
                                                                                          to_user_id))

    try:
        prepaid_record = create_prepaid(channel, order_id, to_user_map.account_user_id, amount,
                                        client_callback_url, client_notify_url)
        return response.success(sn=prepaid_record.sn)
    except Exception as e:
        logger.exception(e)
        return response.fail(code=1, msg=e.message)
