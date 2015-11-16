# coding=utf-8
from __future__ import unicode_literals

from flask import request, render_template, redirect, url_for
from . import checkout_entry_mod as mod
from pytoolbox.util.log import get_logger
from pub_site import pay_client, csrf
from flask.ext.login import current_user, login_required
from .zyt_forms import ZytPayForm
from .commons import payment_failed
from . import utils
from .utils import get_template
from decimal import Decimal


logger = get_logger(__name__)


@mod.route('/zyt_pay/', methods=['POST'])
@csrf.exempt
@pay_client.verify_request
def zyt_pay():
    is_verify_pass = request.is_verify_pass
    if not is_verify_pass:
        return "VERIFY ERROR."
    params = request.params

    sn = params['_sn']

    token = utils.gen_payment_token(sn)

    return redirect(url_for('checkout_entry.zyt_do_pay', sn=sn, token=token))


@mod.route('/zyt_pay/<sn>/<token>', methods=['GET', 'POST'])
@login_required
def zyt_do_pay(sn, token):
    if not utils.check_payment_token(sn, token):
        return render_template(get_template("checkout/info"), msg="支付链接过期，请重新请求支付")

    result = pay_client.get_payment_info(sn)
    if not pay_client.is_success_result(result):
        return payment_failed(result)
    info = result.data['info']
    if info['state'] != 'CREATED':
        return render_template(get_template("checkout/info"), msg="该订单已支付, 如失败，请重新请求支付")

    amount = Decimal(info['amount'])
    user_id = current_user.user_id
    balance = pay_client.app_query_user_available_balance(user_id)
    if amount > balance:
        return render_template(get_template("checkout/info"), msg="自游通余额不足")

    form = ZytPayForm()
    if form.validate_on_submit():
        sn = info['sn']
        result = 'SUCCESS' if pay_client.zyt_pay(sn, user_id) else ''
        return pay_client.web_payment_callback(sn, result)

    return render_template('checkout/zyt_pay_web.html', form=form, info=info,
                           balance='%.2f' % pay_client.app_query_user_available_balance(user_id))
