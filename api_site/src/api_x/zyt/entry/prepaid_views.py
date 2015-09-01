# coding=utf-8
from __future__ import unicode_literals
from api_x.utils import response
from api_x.zyt.biz import prepaid
from api_x.constant import TransactionType
from api_x.zyt.user_mapping import get_user_domain_by_name

from flask import request, url_for
from api_x.config import etc as config
from . import biz_entry_mod as mod
from pytoolbox.util.log import get_logger
from api_x.utils.entry_auth import verify_request


logger = get_logger(__name__)


@mod.route('/prepaid', methods=['POST'])
@verify_request('prepaid')
def prepaid():
    data = request.values
    channel = request.channel
    to_user_id = data['to_user_id']
    to_domain_name = data.get('to_domain_name')
    amount = data['amount']
    client_callback_url = data['callback_url']
    client_notify_url = data['notify_url']

    if not to_domain_name:
        to_user_map = channel.get_user_map(to_domain_name)
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
        prepaid_record = prepaid.create_prepaid(channel, to_user_map.account_user_id, amount,
                                                client_callback_url, client_notify_url)
        pay_url = config.HOST_URL + url_for('biz_entry.prepaid_cashier_desk',
                                            source=TransactionType.PREPAID, sn=prepaid_record.sn)
        return response.success(sn=prepaid_record.sn, pay_url=pay_url)
    except Exception as e:
        logger.exception(e)
        return response.fail(code=1, msg=e.message)
