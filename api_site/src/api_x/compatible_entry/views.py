# coding=utf-8
from __future__ import unicode_literals
from api_x.zyt.user_mapping import get_channel_by_name, get_or_create_account_user
from api_x.zyt.biz import payment
from api_x.zyt.biz import refund

from flask import request, url_for
from api_x.utils import response
from . import compatible_entry_mod as mod
from pytoolbox.util.log import get_logger
from api_x.zyt.biz.models import PaymentType
from api_x.config import etc as config

logger = get_logger(__name__)


@mod.route('/secured/pre-pay', methods=['POST'])
def secured_pre_pay():
    data = request.values
    channel_id = data['client_id']
    payer_user_id = data['payer_user_id']
    payee_user_id = data['payee_user_id']
    desc = _generate_order_desc(data['order_no'], data['order_name'], data['payer_user_name'])
    order = Order(data['activity_id'], data['order_no'], data['order_name'], desc, data['ordered_on'])
    amount = data['amount']
    client_callback_url = data['client_callback_url']
    client_async_callback_url = data['client_async_callback_url']

    logger.info('receive secure pre pay: {0}'.format({k: v for k, v in data.items()}))
    # FIXME
    # NOTE: this is for lvye huodong only.
    if channel_id != "1":
        return response.fail()

    channel_name = 'lvye_huodong'
    channel = get_channel_by_name(channel_name)
    if channel is None:
        return response.fail(msg='channel not exits: [{0}]'.format(channel_name))

    payer_id = get_or_create_account_user(channel.user_domain_id, payer_user_id)
    payee_id = get_or_create_account_user(channel.user_domain_id, payee_user_id)

    try:
        payment_record = payment.find_or_create_payment(PaymentType.GUARANTEE, payer_id, payee_id, channel,
                                                        order.no, order.name, order.category, order.desc, amount,
                                                        client_callback_url, client_async_callback_url)
        pay_url = config.HOST_URL + url_for('biz_entry.cashier_desk', sn=payment_record.sn)

        return response.success(pay_url=pay_url)
    except Exception as e:
        logger.exception(e)
        return response.fail(code=1, msg=e.message)


@mod.route('/secured/refund', methods=['POST'])
def apply_for_refund():
    data = request.values
    channel_id = data['client_id']
    order_no = data['order_no']
    amount = data['amount']
    callback_url = data['callback_url']

    logger.info('receive secured refund: {0}'.format({k: v for k, v in data.items()}))
    # FIXME
    # NOTE: this is for lvye huodong only.
    if channel_id != "1":
        return response.fail()

    channel_name = 'lvye_huodong'
    channel = get_channel_by_name(channel_name)
    if channel is None:
        return response.fail(msg='channel not exits: [{0}]'.format(channel_name))

    try:
        refund_record = refund.apply_to_refund(channel, order_no, amount, callback_url, data)
        return response.accepted(id=refund_record.sn)
    except Exception as e:
        logger.exception(e)
        return response.fail(code=1, msg=e.message)


@mod.route('/secured/clients/<int:channel_id>/orders/<order_id>/confirm-pay', methods=['PUT'])
def confirm_to_pay(channel_id, order_id):
    # FIXME
    # NOTE: this is for lvye huodong only.
    if channel_id != "2":
        return response.fail()

    channel_name = 'lvye_huodong'
    channel = get_channel_by_name(channel_name)
    if channel is None:
        return response.fail(msg='channel not exits: [{0}]'.format(channel_name))

    try:
        payment.confirm_payment(channel, order_id)
        return response.success()
    except Exception as e:
        return response.bad_request(msg=e.message)


def _generate_order_desc(order_no, order_name, payer_name):
    return u"{1}[{0}]；付款人：{2}".format(order_no, order_name, payer_name)


class Order(object):
    def __init__(self, activity_id, no, name, desc, created_on):
        self.activity_id = activity_id
        self.no = no
        self.name = name
        self.desc = desc
        self.created_on = created_on
        self.category = u'虚拟商品'