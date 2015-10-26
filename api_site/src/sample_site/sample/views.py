# coding=utf-8
from __future__ import unicode_literals, print_function

from decimal import Decimal
from flask import request, render_template, redirect, url_for, Response
from . import sample_mod as mod
from sample_site import config
from sample_site.utils import generate_order_id
from sample_site import pay_client
from pytoolbox.util.log import get_logger
import json


logger = get_logger(__name__)


@mod.route('/', methods=['GET'])
def index():
    channel_name = config.PayClientConfig.CHANNEL_NAME
    payer_user_name = 'webee'
    payer = '96355632'
    payee = config.PAYEE

    payer_balance = pay_client.app_query_user_balance(payer)
    payee_balance = pay_client.app_query_user_balance(payee)
    bankcards = pay_client.app_list_user_bankcards(payee)
    return render_template('sample/index.html', channel=channel_name, payer_user_name=payer_user_name,
                           payer=payer, payee=payee, payer_balance=payer_balance, payee_balance=payee_balance,
                           bankcards=bankcards)


@mod.route('/pay', methods=['POST'])
def pay():
    """支付一分钱"""
    payer = '96355632'

    memo = request.values.get('memo', '')
    use_zyt_pay = request.values.get('use_zyt_pay')
    payee = request.values.get('other_payee')
    payee = payee or request.values['payee']
    payee_domain_name = request.values['payee_domain_name']
    amount = Decimal(request.values['amount'])
    payment_type = request.values['payment_type']
    params = {
        'payer_user_id': payer,
        'payee_user_id': payee,
        'payee_domain_name': payee_domain_name,
        'order_id': request.values.get('order_id') or generate_order_id(),
        'product_name': '测试{1}支付{0}元_{2}'.format(amount, '担保' if payment_type == 'GUARANTEE' else '', memo),
        'product_category': '测试',
        'product_desc': '用于测试的商品',
        'amount': amount,
        'callback_url': config.HOST_URL + url_for('.pay_result'),
        'notify_url': '',
        'payment_type': payment_type
    }

    print("order_id: {0}".format(params['order_id']))

    sn = pay_client.prepay(params, ret_sn=True)
    if sn is None:
        return redirect(url_for('.index'))

    if use_zyt_pay:
        return Response(pay_client.web_zyt_pay(sn))

    return redirect(pay_client.web_checkout_url(sn))


@mod.route('/pay_result', methods=['POST'])
@pay_client.verify_request
def pay_result():
    is_verify_pass = request.is_verify_pass
    if not is_verify_pass:
        return render_template('sample/info.html', title='支付结果', msg="请求异常")
    data = request.params

    return render_template('sample/pay_result.html', title='支付结果', data=data)


@mod.route('/pay/guarantee_payment/confirm', methods=['POST'])
def confirm_guarantee_payment():
    data = request.values
    order_id = data['order_id']

    result = pay_client.confirm_guarantee_payment(order_id, ret_result=True)

    return render_template('sample/info.html', title='确认担保支付结果',
                           msg=json.dumps({'status_code': result.status_code, 'data': result.data}))


@mod.route('/refund', methods=['POST'])
def refund():
    suggest_result = request.values['suggest_result']
    params = {
        'order_id': request.values['order_id'],
        'amount': Decimal(request.values['amount']),
        'notify_url': ''
    }
    if suggest_result:
        # for test.
        params['result'] = suggest_result

    result = pay_client.refund(params=params, ret_result=True)
    return render_template('sample/info.html', title='退款结果',
                           msg=json.dumps({'status_code': result.status_code, 'data': result.data}))


@mod.route('/withdraw', methods=['POST'])
def withdraw():
    user_id = config.PAYEE

    suggest_result = request.values['suggest_result']
    params = {
        'bankcard_id': request.values['bankcard_id'],
        'amount': Decimal(request.values['amount']),
        'notify_url': ''
    }

    if suggest_result:
        # for test.
        params['result'] = suggest_result

    result = pay_client.app_withdraw(user_id, params=params, ret_result=True)
    return render_template('sample/info.html', title='提现结果',
                           msg=json.dumps({'status_code': result.status_code, 'data': result.data}))
