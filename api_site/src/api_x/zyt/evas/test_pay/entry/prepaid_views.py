# coding=utf-8
from __future__ import unicode_literals
from api_x.zyt.biz.models import PaymentType

from flask import Response, abort, url_for, request, jsonify, redirect, render_template
from . import test_pay_entry_mod as mod
from api_x.config import etc as config
from api_x.config import test_pay as test_pay_config
from api_x.zyt.biz.transaction import get_tx_by_sn
from api_x.zyt.biz.payment import get_payment_by_tx_id, update_payment_info, succeed_payment


@mod.route("/prepaid", methods=["POST"])
def prepaid():
    """充值入口"""
    transaction = get_tx_by_sn(sn)
    if transaction is None:
        abort(404)
    payment_record = get_payment_by_tx_id(transaction.id)

    form_submitted = pay(payment_record)
    return Response(form_submitted, status=200, mimetype='text/html')


@mod.route("/test_pay/pay/result", methods=["POST"])
def test_pay_pay_result():
    """支付页面回调, 更多操作可由notify完成，这里只是返回callback"""
    data = request.values
    sn = data['order_no']
    result = data['result']

    transaction = get_tx_by_sn(sn)
    payment_record = get_payment_by_tx_id(transaction.id)

    if result == 'SUCCESS':
        if payment_record.client_callbackk_url:
            return redirect(payment_record.client_callbackk_url)
        return render_template('info.html', title='支付结果', msg='支付成功')


@mod.route("/test_pay/pay/notify", methods=["POST"])
def test_pay_pay_notify():
    data = request.values
    sn = data['order_no']
    vas_sn = data['sn']
    result = data['result']
    amount = data['amount']

    transaction = get_tx_by_sn(sn)
    payment_record = get_payment_by_tx_id(transaction.id)

    if result == 'SUCCESS':
        update_payment_info(payment_record.id, 'test_pay', vas_sn)
        if payment_record.type == PaymentType.DIRECT:
            succeed_payment()
            pass
        elif payment_record.type == PaymentType.SECURED:
            pass
            # TODO
            # notify
    return jsonify(code=0)


def pay(payment_record):
    return_url = config.HOST_URL + url_for('entry.test_pay_pay_result')
    notify_url = config.HOST_URL + url_for('entry.test_pay_pay_notify')
    req_params = {
        'merchant_id': test_pay_config.MERCHANT_ID,
        'order_no': payment_record.sn,
        'product_name': payment_record.product_name,
        'amount': payment_record.amount,
        'return_url': return_url,
        'notify_url': notify_url
        }
    return _generate_submit_form(req_params)


def _generate_submit_form(req_params):
    submit_page = '<form id="payBillForm" action="{0}" method="POST">'.format(test_pay_config.Pay.URL)
    for key in req_params:
        submit_page += '''<input type="hidden" name="{0}" value='{1}' />'''.format(key, req_params[key])
    submit_page += '<input type="submit" value="Submit" style="display:none" /></form>'
    submit_page += '<script>document.forms["payBillForm"].submit();</script>'
    return submit_page
