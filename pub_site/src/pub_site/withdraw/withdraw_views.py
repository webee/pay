# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from flask.ext.login import login_required, current_user
from flask import render_template, url_for, redirect, g, current_app
from . import withdraw_mod as mod
from pytoolbox.util.dbe import from_db
from tools.mylog import get_logger
from . import WITHDRAW_COMMISSION
from .forms import BindCardForm, WithdrawForm
from identifying_code_manager import generate_and_send_identifying_code
from pay_client import PayClient
from flask import flash
from datetime import datetime
from ..constant import PayType


logger = get_logger(__name__)


@mod.before_app_first_request
def register_filters():
    bank_names = ('上海银行', '中信银行', '中国人民银行', '中国农业银行', '中国工商银行', '中国建设银行', '中国银行', '交通银行',
                  '兴业银行', '北京银行', '华夏银行', '天津银行', '工商银行', '平安银行', '广发银行', '光大银行', '恒丰银行',
                  '招商银行', '民生银行', '浙商银行', '浦发银行', '渤海银行', '邮政储蓄', '重庆银行')

    def _to_bank_logo(value):
        return "images/%s.png" % (value if value in bank_names else '其他银行')

    def _to_bankcard_mask(value):
        return u"%s **** **** %s" % (value[:4], value[-4:])

    current_app.jinja_env.filters['toBankcardMask'] = _to_bankcard_mask
    current_app.jinja_env.filters['toBankLogo'] = _to_bank_logo


@mod.before_request
def set_current_channel():
    g.current_channel = 'withdraw'


@mod.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    balance = PayClient().get_balance()['data']['balance']
    bankcards = PayClient().get_bankcards()['data']
    if len(bankcards) == 0:
        return redirect(url_for('.bind_card'))
    form = WithdrawForm()
    selected_card = _find_selected_card(bankcards, long(form.bankcard.data))
    if form.validate_on_submit():
        actual_amount = form.amount.data - WITHDRAW_COMMISSION
        result = PayClient().withdraw(actual_amount, form.bankcard.data, "callback_url")
        if result['status_code'] != 202:
            flash(u"提现失败，请核实账户信息！", category="error")
            return redirect(url_for('.withdraw'))
        _charge_for_commission()
        _update_preferred_card(form.bankcard.data)
        success_message = u"提现 %s元 申请成功！绿野将于3-5个工作日内审核并处理。" % actual_amount
        flash(success_message, category="success")
        return redirect(url_for('main.index'))
    return render_template('withdraw/withdraw.html', balance=balance, bankcards=bankcards,
                           selected_card=selected_card, form=form)


@mod.route('/withdraw/bind-card', methods=['GET', 'POST'])
@login_required
def bind_card():
    form = BindCardForm()
    if form.validate_on_submit():
        result = _do_bind_card(form)
        if result['status_code'] != 201:
            flash(u"银行卡绑定失败，请稍后再试。", category="error")
            return redirect(url_for('.bind_card'))
        _update_preferred_card(result['data']['id'])
        return redirect(url_for('.withdraw'))
    return render_template('withdraw/bind-card.html', form=form)


@mod.route('/withdraw/<transaction_id>/result')
@login_required
def show_withdraw_result_page(transaction_id):
    return render_template('withdraw/show-withdraw-result.html')


@mod.route('/withdraw/generate-identifying-code', methods=['POST'])
@login_required
def generate_identifying_code():
    resp = generate_and_send_identifying_code()
    return resp.content, resp.status_code


def _update_preferred_card(card_id):
    db = from_db()
    current_user_id = current_user.user_id
    user_id = db.exists('select user_id from preferred_card where user_id=%(user_id)s', user_id=current_user_id)
    if user_id == 0:
        db.insert('preferred_card', {"user_id": current_user_id, "bankcard_id": card_id})
    else:
        db.execute('update preferred_card set bankcard_id=%(card_id)s where user_id=%(user_id)s',
                   card_id=card_id, user_id=current_user_id)


def _charge_for_commission():
    order = {
        "name": "pay_to_lvye",
        "pay_type": PayType.BY_BALANCE,
        "description": "commission for withdraw",
        "amount": WITHDRAW_COMMISSION,
        "created_on": datetime.now().isoformat()
    }
    order_id = from_db().insert('zyt_order', order, returns_id=True)
    PayClient().transfer_to_lvye(WITHDRAW_COMMISSION, order_id, order["description"])


def _do_bind_card(form):
    card_number = form.card_number.data
    account_name = form.name.data
    province_code = form.province.data
    city_code = form.city.data
    branch_bank_name = form.subbranch_name.data
    return PayClient().bind_bankcards(
        card_number=card_number,
        account_name=account_name,
        province_code=province_code,
        city_code=city_code,
        branch_bank_name=branch_bank_name
    )


def _find_selected_card(bankcards, selected_card_id):
    for card in bankcards:
        if card['id'] == selected_card_id:
            return card
    return None