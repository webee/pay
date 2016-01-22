# coding=utf-8
from __future__ import unicode_literals, print_function

from decimal import Decimal
from flask import request, render_template, url_for, redirect
from . import sample_mod as mod
from sample_site import config
from sample_site import pay_client
from pytoolbox.util.log import get_logger


logger = get_logger(__name__)


@mod.route('/prepaid', methods=['POST'])
def prepaid():
    """充值"""
    to_user_id = request.values.get('to_user_id') or '96355632'
    to_domain_name = request.values.get('to_domain_name')
    amount = Decimal(request.values['amount'])
    callback_url = config.HOST_URL + url_for('.prepaid_result')
    use_old_pay = request.values.get('use_old_pay')

    sn = pay_client.preprepaid(to_user_id=to_user_id, amount=amount,
                               to_domain_name=to_domain_name, callback_url=callback_url, notify_url="")

    if sn is None:
        return render_template('sample/info.html', title='充值结果', msg="请求支付失败")

    if use_old_pay:
        return redirect(pay_client.web_checkout_url(sn, pay_client.constant.TransactionType.PREPAID))
    return redirect(pay_client.checkout_url(sn))


@mod.route('/prepaid_result', methods=['POST'])
@pay_client.verify_request
def prepaid_result():
    is_verify_pass = request.is_verify_pass
    if not is_verify_pass:
        return render_template('sample/info.html', title='充值结果', msg="请求异常")
    data = request.params

    return render_template('sample/prepaid_result.html', title='充值结果', data=data)
