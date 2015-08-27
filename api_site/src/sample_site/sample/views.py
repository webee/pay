# coding=utf-8
from __future__ import unicode_literals, print_function

from decimal import Decimal
from flask import request, render_template, redirect, url_for, flash
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
    payer = 'webee'
    payee = config.PAYEE

    payee_account_user_id = pay_client.get_account_user_id(payee)
    balance = pay_client.get_user_balance(payee)
    bankcards = pay_client.list_user_bankcards(payee)
    return render_template('sample/index.html', channel=channel_name, payer=payer, payee=payee,
                           payee_account_user_id=payee_account_user_id, balance=balance,
                           bankcards=bankcards)


@mod.route('/pay', methods=['POST'])
def pay():
    """支付一分钱"""
    payer = '96355632'
    payee = config.PAYEE

    amount = Decimal(request.values['amount'])
    payment_type = request.values['payment_type']
    params = {
        'payer_user_id': payer,
        'payee_user_id': payee,
        'order_id': request.values.get('order_id') or generate_order_id(),
        'product_name': '测试{1}支付{0}元'.format(amount, '担保' if payment_type == 'GUARANTEE' else ''),
        'product_category': '测试',
        'product_desc': '用于测试的商品',
        'amount': amount,
        'callback_url': config.HOST_URL + url_for('.pay_result'),
        'notify_url': '',
        'payment_type': payment_type
    }

    print("order_id: {0}".format(params['order_id']))

    data = pay_client.prepay(params)
    if data['ret']:
        return redirect(data['pay_url'])
    else:
        return render_template('sample/info.html', title='请求支付结果', msg=json.dumps(data))
    logger.info('prepay ret: {0}'.format(data))
    flash('请求支付失败')
    return redirect(url_for('.index'))


@mod.route('/pay_result', methods=['POST'])
@pay_client.verify_request
def pay_result():
    is_verify_pass = request.is_verify_pass
    if not is_verify_pass:
        return render_template('sample/info.html', title='支付结果', msg="请求异常")
    data = request.params
    print(data)

    return render_template('sample/pay_result.html', title='支付结果', data=data)




@mod.route('/pay/guarantee_payment/confirm', methods=['POST'])
def confirm_guarantee_payment():
    data = request.values
    order_id = data['order_id']

    data = pay_client.confirm_guarantee_payment(order_id)
    return render_template('sample/info.html', title='确认担保支付结果', msg=json.dumps(data))


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

    logger.info('refund: {0}'.format(params))
    data = pay_client.refund(params)
    return render_template('sample/info.html', title='退款结果', msg=json.dumps(data))


@mod.route('/withdraw', methods=['POST'])
def withdraw():
    user_id = config.PAYEE

    use_test_pay = request.values.get('use_test_pay')
    suggest_result = request.values['suggest_result']
    params = {
        'bankcard_id': request.values['bankcard_id'],
        'amount': Decimal(request.values['amount']),
        'notify_url': ''
    }
    if use_test_pay:
        # for test.
        params['use_test_pay'] = '1'

    if suggest_result:
        # for test.
        params['result'] = suggest_result

    logger.info('withdraw: {0}'.format(params))
    data = pay_client.withdraw(user_id, params)
    return render_template('sample/info.html', title='提现结果', msg=json.dumps(data))


@mod.route('/prepaid', methods=['GET'])
def prepaid():
    """充值"""
    return render_template('sample/prepaid.html', user_id=2, prepaid_url=config.PayClientConfig.PREPAID_URL)
