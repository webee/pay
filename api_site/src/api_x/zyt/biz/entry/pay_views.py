# coding=utf-8
from __future__ import unicode_literals
from api_x.utils import response
from api_x.zyt.biz import pay
from api_x.zyt.biz.models import TransactionType
from api_x.zyt.user_mapping import get_user_domain_by_name, get_channel_by_name

from flask import request
from . import biz_entry_mod as mod
from pytoolbox.util.log import get_logger
from api_x.utils.entry_auth import verify_request, prepay_entry
from api_x.zyt.biz.models import PaymentType
from api_x.zyt.biz.pay.error import AlreadyPaidError


logger = get_logger(__name__)


@mod.route('/prepay', methods=['POST'])
@verify_request('prepay')
@prepay_entry(TransactionType.PAYMENT)
def prepay():
    data = request.values
    channel = request.channel
    payer_user_id = data['payer_user_id']
    payee_user_id = data['payee_user_id']
    payee_domain_name = data.get('payee_domain_name')
    order_id = data['order_id']
    product_name = data['product_name']
    product_category = data['product_category']
    product_desc = data['product_desc']
    amount = data['amount']
    client_callback_url = data['callback_url']
    client_notify_url = data['notify_url']
    payment_type = data['payment_type']

    # check
    if payment_type not in [PaymentType.DIRECT, PaymentType.GUARANTEE]:
        return response.fail(msg="payment_type [{0}] not supported.".format(payment_type))

    payer_user_map = channel.get_add_user_map(payer_user_id)
    if not payee_domain_name:
        # 默认payee用户域和payer是一致的
        payee_user_map = channel.get_add_user_map(payee_user_id)
    else:
        # 指定不同的payee用户域
        payee_domain = get_user_domain_by_name(payee_domain_name)
        if payee_domain is None:
            return response.fail(msg="domain [{0}] not exists.".format(payee_domain_name))
        payee_user_map = payee_domain.get_user_map(payee_user_id)
        if payee_user_map is None:
            return response.fail(msg="payee with domain [{0}] user [{1}] not exists.".format(payee_domain_name,
                                                                                             payee_user_id))

    try:
        payment_record = pay.find_or_create_payment(channel, payment_type,
                                                    payer_user_map.account_user_id, payee_user_map.account_user_id,
                                                    order_id, product_name, product_category, product_desc, amount,
                                                    client_callback_url, client_notify_url)
        return payment_record.tx
    except AlreadyPaidError as e:
        logger.exception(e)
        return response.fail(msg=e.message)
    except Exception as e:
        logger.exception(e)
        return response.fail(code=1, msg=e.message)


@mod.route('/prepay/<order_channel>/<order_id>/', methods=['GET'])
@verify_request('prepay_channel_order')
@prepay_entry(TransactionType.PAYMENT)
def prepay_channel_order(order_channel, order_id):
    """超级支付接口"""
    channel = get_channel_by_name(order_channel)
    if channel is None:
        return response.refused('bad channel: [{0}]'.format(order_channel))

    try:
        payment_record = pay.find_payment(channel, order_id)
        return payment_record.tx
    except AlreadyPaidError as e:
        logger.exception(e)
        return response.fail(msg=e.message)
    except Exception as e:
        logger.exception(e)
        return response.fail(code=1, msg=e.message)


@mod.route('/pay/guarantee_payment/confirm', methods=['POST'])
@verify_request('confirm_guarantee_payment')
def confirm_guarantee_payment():
    from api_x.utils import response
    data = request.params
    channel = request.channel
    order_id = data['order_id']

    try:
        pay.confirm_payment(channel, order_id)
        return response.success()
    except Exception as e:
        logger.exception(e)
        return response.bad_request(msg=e.message)
