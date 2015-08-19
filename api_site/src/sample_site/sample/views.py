# coding=utf-8
from __future__ import unicode_literals, print_function

from decimal import Decimal
from flask import request, render_template, redirect, url_for
from . import sample_mod as mod
from sample_site import config
from sample_site.utils import generate_order_id
from sample_site import pay_client
from tools.mylog import get_logger


logger = get_logger(__name__)


@mod.route('/', methods=['GET'])
def index():
    """支付一分钱"""
    channel_name = config.PayAPI.CHANNEL_NAME
    payer = 'webee'
    payee = 'test001'

    payee_account_user_id = pay_client.get_account_user_id(payee)
    balance = pay_client.get_user_balance(payee)
    return render_template('sample/index.html', channel=channel_name, payer=payer, payee=payee,
                           payee_account_user_id=payee_account_user_id, balance=balance)


@mod.route('/pay', methods=['POST'])
def pay():
    """支付一分钱"""
    channel_name = config.PayAPI.CHANNEL_NAME
    payer = 'webee'
    payee = 'test001'

    amount = Decimal(request.values['amount'])
    payment_type = request.values['payment_type']
    params = {
        'channel_name': channel_name,
        'payer_user_id': payer,
        'payee_user_id': payee,
        'order_id': request.values.get('order_id') or generate_order_id(),
        'product_name': '测试{1}支付{0}元'.format(amount, '担保' if payment_type == 'GUARANTEE' else ''),
        'product_category': '测试',
        'product_desc': '[{0}]用于测试的商品'.format(channel_name),
        'amount': amount,
        'client_callback_url': config.HOST_URL + url_for('.index'),
        'client_notify_url': '',
        'payment_type': payment_type
    }

    print("order_id: {0}".format(params['order_id']))

    data = pay_client.request_prepay(params)
    return redirect(data['pay_url'])


@mod.route('/pay/guarantee_payment/confirm', methods=['POST'])
def confirm_guarantee_payment():
    channel_name = config.PayAPI.CHANNEL_NAME
    params = {
        'channel_name': channel_name,
        'order_id': request.values['order_id']
    }

    data = pay_client.request_confirm_guarantee_payment(params)
    print('confirm guarantee pay: {0}'.format(data))
    return redirect(url_for('sample.index'))


@mod.route('/refund', methods=['POST'])
def refund():
    suggest_result = request.values['suggest_result']
    channel_name = config.PayAPI.CHANNEL_NAME
    params = {
        'channel_name': channel_name,
        'order_id': request.values['order_id'],
        'amount': Decimal(request.values['amount']),
        'notify_url': ''
    }
    if suggest_result:
        # for test.
        params['result'] = suggest_result

    logger.info('refund: {0}'.format(params))
    req = pay_client.request_refund(params)
    return render_template('sample/info.html', title='退款结果', msg=req.content)


@mod.route('/withdraw', methods=['POST'])
def withdraw():
    user_id = 'test001'

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
    req = pay_client.request_withdraw(user_id, params)
    return render_template('sample/info.html', title='提现结果', msg=req.content)


@mod.route('/prepaid', methods=['GET'])
def prepaid():
    """充值"""
    return render_template('sample/prepaid.html', user_id=2, prepaid_url=config.PayAPI.PREPAID_URL)
