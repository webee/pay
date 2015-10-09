# coding=utf-8
from __future__ import unicode_literals, print_function

from decimal import Decimal
from flask import request, url_for, jsonify
from . import app_server_mod as mod
from sample_site import config
from sample_site.utils import generate_order_id
from sample_site import pay_client
from pytoolbox.util.log import get_logger


logger = get_logger(__name__)


@mod.route('/prepay', methods=['POST'])
def prepay():
    data = request.values

    logger.info("app prepay: {0}".format(data))
    payer = data['payer']
    payee = data['payee']
    payee_domain_name = data['payee_domain_name']
    amount = Decimal(data['amount'])
    payment_type = data['payment_type']
    params = {
        'payer_user_id': payer,
        'payee_user_id': payee,
        'payee_domain_name': payee_domain_name,
        'order_id': request.values.get('order_id') or generate_order_id(),
        'product_name': '测试{1}支付{0}元'.format(amount, '担保' if payment_type == 'GUARANTEE' else ''),
        'product_category': '测试',
        'product_desc': '用于测试的商品',
        'amount': amount,
        'callback_url': config.HOST_URL + url_for('sample.pay_result'),
        'notify_url': '',
        'payment_type': payment_type
    }

    print("order_id: {0}".format(params['order_id']))
    sn = pay_client.prepay(params, ret_sn=True)

    return jsonify(ret=True, sn=sn)
