# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from decimal import Decimal
from flask import g, render_template, redirect, url_for, flash, request
from flask.ext.login import current_user
from . import pay_to_lvye_mod as mod
from pub_site.pay_to_lvye.forms import PayToLvyeForm
from pub_site import pay_client
from pytoolbox.util.log import get_logger
from . import dba
from pub_site import config
from pub_site.auth.utils import login_required

_logger = get_logger(__name__, level=os.getenv('LOG_LEVEL', 'INFO'))


@mod.before_request
def set_current_channel():
    g.current_channel = 'pay_to_lvye'


@mod.route('/pay_to_lvye', methods=['GET', 'POST'])
@login_required
def pay_to_lvye():
    user_id = current_user.user_id
    form = PayToLvyeForm()
    if form.validate_on_submit():
        amount = Decimal(form.amount.data)
        pay_channel = form.pay_channel.data
        comment = form.comment.data
        pay_to_lvye_record = dba.add_pay_to_lvye_record(user_id, amount, "付款给绿野", comment)
        return _do_pay(pay_to_lvye_record, pay_channel)
    return render_template('pay/pay.html', form=form,
                           balance='%.2f' % pay_client.app_query_user_available_balance(user_id))


def _handle_result(result, process):
    if result['status_code'] == 200:
        return process()
    else:
        flash(u"付款给绿野支付失败！", category="error")
        return redirect(url_for('.pay'))


def _do_pay(pay_to_lvye_record, pay_channel):
    params = {
        'payer_user_id': pay_to_lvye_record.user_id,
        'payee_domain_name': config.LVYE_CORP_DOMAIN_NAME,
        'payee_user_id': config.LVYE_USER_NAME,
        'order_id': pay_to_lvye_record.order_id,
        'product_name': '{0}: {1}元'.format(pay_to_lvye_record.name, pay_to_lvye_record.amount),
        'product_category': pay_to_lvye_record.name,
        'product_desc': pay_to_lvye_record.comment,
        'amount': pay_to_lvye_record.amount,
        'callback_url': config.HOST_URL + url_for('notify.pay_result'),
        'notify_url': '',
        'payment_type': pay_client.constant.PaymentType.DIRECT
    }

    print("order_id: {0}".format(params['order_id']))

    sn = pay_client.prepay(params, ret_sn=True)
    if sn is None:
        return redirect(url_for('.pay_to_lvye'))
    if pay_channel == 'ZYT':
        return pay_client.web_zyt_pay(sn)
    return redirect(pay_client.checkout_url(sn))
