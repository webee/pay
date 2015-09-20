# coding=utf-8
from __future__ import unicode_literals
from api_x.utils import response
from api_x.zyt.biz import payment
from api_x.constant import PaymentTxState
from api_x.zyt.biz.models import TransactionType
from api_x.zyt.user_mapping import get_user_domain_by_name

from flask import request, url_for
from api_x.config import etc as config
from . import biz_entry_mod as mod
from pytoolbox.util.log import get_logger
from api_x.utils.entry_auth import verify_request
from api_x.zyt.biz.models import PaymentType


logger = get_logger(__name__)


@mod.route('/prepay', methods=['POST'])
@verify_request('prepay')
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
        payment_record = payment.find_or_create_payment(channel, payment_type,
                                                        payer_user_map.account_user_id, payee_user_map.account_user_id,
                                                        order_id, product_name, product_category, product_desc, amount,
                                                        client_callback_url, client_notify_url)
        if payment_record.tx.state != PaymentTxState.CREATED:
            return response.fail(msg="order already paid.")

        # FIXME: 不直接返回pay_url, 修改pay_client, pay_url作为web支付方式在客户端确定
        pay_url = config.HOST_URL + url_for('web_checkout_entry.cashier_desk', source=TransactionType.PAYMENT, sn=payment_record.sn)
        return response.success(sn=payment_record.sn, pay_url=pay_url)
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
        payment.confirm_payment(channel, order_id)
        return response.success()
    except Exception as e:
        logger.exception(e)
        return response.bad_request(msg=e.message)
