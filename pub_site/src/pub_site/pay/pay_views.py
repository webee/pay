# -*- coding: utf-8 -*-

from flask import g, render_template, redirect, url_for, flash
from flask.ext.login import current_user
from . import pay_mod as mod
from ..constant import PayType
from pub_site.pay.forms import PayForm
from pub_site.withdraw.pay_client import PayClient
from pytoolbox.util.dbs import from_db
from datetime import datetime
from pytoolbox.util.log import get_logger
import os
from pub_site.auth.utils import login_required

_logger = get_logger(__name__, level=os.getenv('LOG_LEVEL', 'INFO'))


@mod.before_request
def set_current_channel():
    g.current_channel = 'pay'


@mod.route('/pay', methods=['GET', 'POST'])
@login_required
def pay():
    form = PayForm()
    if form.validate_on_submit():
        order = _create_order(form.amount.data, form.pay_type.data, form.comment.data)
        return _pay(order)
    return render_template('pay/pay.html', form=form)


@mod.route('/pay-success', methods=['GET'])
@login_required
def pay_succeed():
    flash(u"付款给绿野支付成功！", category="success")
    return redirect(url_for("main.index"))


def _create_order(amount, pay_type, comment):
    order = {
        "name": u"付款给绿野",
        "user_id": current_user.user_id,
        "pay_type": pay_type,
        "description": (u"付款给绿野：%s" % comment),
        "amount": amount,
        "created_on": datetime.now().isoformat()

    }
    order_id = from_db().insert('zyt_order', order, returns_id=True)
    order["id"] = order_id
    return order


def _handle_result(result, process):
    if result['status_code'] == 200:
        return process()
    else:
        flash(u"付款给绿野支付失败！", category="error")
        return redirect(url_for('.pay'))


def _pay(order):
    if order["pay_type"] == PayType.BY_BALANCE:
        result = PayClient().transfer_to_lvye(order["amount"], order_id=order["id"], order_info=order["description"])

        def succeed_handler():
            flash(u"付款给绿野支付成功！", category="success")
            return redirect(url_for('main.index'))

        return _handle_result(result, succeed_handler)
    if order["pay_type"] == PayType.BY_BANKCARD:
        result = PayClient().pay_to_lvye(order["amount"], order_id=order["id"], order_name=order["name"],
                                         order_description=order["description"], create_on=order["created_on"],
                                         callback_url=url_for('.pay_succeed', _external=True))
        _logger.info("pay result: %s" % result['data']['pay_url'])
        succeed_handler = lambda: redirect(result['data']['pay_url'])
        return _handle_result(result, succeed_handler)