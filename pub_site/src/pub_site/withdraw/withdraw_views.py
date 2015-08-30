# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from flask import render_template, url_for, redirect, g, current_app, flash, request, jsonify
from flask.ext.login import current_user
from decimal import Decimal
from pytoolbox.util.log import get_logger
from pub_site import pay_client
from pub_site.auth.utils import login_required
from . import withdraw_mod as mod, dba
from .forms import BindCardForm, WithdrawForm
from pub_site.sms import sms
from pub_site import config
from pub_site.constant import WithdrawState


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
    uid = current_user.user_id
    bankcards = pay_client.app_list_user_bankcards(uid)
    if len(bankcards) == 0:
        return redirect(url_for('.bind_card'))
    form = WithdrawForm(bankcards)
    if form.validate_on_submit():
        user_id = current_user.user_id
        phone_no = current_user.phone_no
        amount = Decimal(form.amount.data)
        bankcard_id = long(form.bankcard.data)
        result = _do_withdraw(user_id, bankcard_id, phone_no, amount, use_test_pay=request.args.get('use_test_pay'))
        if result is None:
            return _withdraw_failed()

        actual_amount = result['actual_amount']
        fee = result['fee']
        return _withdraw_succeed(actual_amount, fee)
    bankcard_id = long(form.bankcard.data) if form.bankcard.data else 0
    return render_template('withdraw/withdraw.html', balance=pay_client.app_query_user_available_balance(uid),
                           bankcards=bankcards, form=form,
                           selected_card=_find_selected_card(bankcards, bankcard_id))


@mod.route('/withdraw_notify', methods=['POST'])
@pay_client.verify_request
def withdraw_notify():
    is_verify_pass = request.is_verify_pass
    if not is_verify_pass:
        return jsonify(code=1)

    data = request.params
    code = data['code']
    sn = data['sn']
    user_id = data['user_id']

    withdraw_record = dba.get_withdraw_record(sn, user_id)
    if withdraw_record is None:
        return jsonify(code=1)

    if code in [0, '0']:
        # 成功
        dba.update_withdraw_state(withdraw_record.sn, withdraw_record.user_id,
                                  WithdrawState.REQUESTED, WithdrawState.SUCCESS)
        msg = "您的提现请求已处理，请等待到账"
    else:
        # 失败
        dba.update_withdraw_state(withdraw_record.sn, withdraw_record.user_id,
                                  WithdrawState.REQUESTED, WithdrawState.FAILED)
        msg = "您的提现请求失败"

    if sms.send(withdraw_record.phone_no, msg):
        return jsonify(code=0)
    return jsonify(code=1)


@mod.route('/withdraw/bind-card', methods=['GET', 'POST'])
@login_required
def bind_card():
    form = BindCardForm()
    if form.validate_on_submit():
        bankcard_id = _do_bind_card(form)
        if bankcard_id is None:
            flash(u"银行卡绑定失败，请稍后再试。", category="error")
            return redirect(url_for('.bind_card'))
        dba.update_user_preferred_card(current_user.user_id, bankcard_id)
        return redirect(url_for('.withdraw'))
    return render_template('withdraw/bind-card.html', form=form)


def _do_bind_card(form):
    user_id = current_user.user_id
    params = {
        "card_no": form.card_number.data.replace(" ", ""),
        "account_name": form.name.data,
        "is_corporate_account": 0,
        "province_code": form.province.data,
        "city_code": form.city.data,
        "branch_bank_name": form.subbranch_name.data
    }
    return pay_client.app_bind_bankcard(user_id, params)


def _find_selected_card(bankcards, selected_card_id):
    for card in bankcards:
        if card['id'] == selected_card_id:
            return card
    if len(bankcards) > 0:
        return bankcards[0]
    return None


def _do_withdraw(user_id, bankcard_id, phone_no, amount, use_test_pay=None):
    notify_url = config.HOST_URL + url_for('.withdraw_notify')
    params = {
        'bankcard_id': bankcard_id,
        'amount': amount,
        'notify_url': notify_url
    }
    if use_test_pay:
        params['use_test_pay'] = 1

    result = pay_client.app_withdraw(user_id, params=params)
    if result is not None:
        dba.update_user_preferred_card(user_id, bankcard_id)
        sn = result['sn']
        actual_amount = result['actual_amount']
        fee = result['fee']
        dba.add_withdraw_record(sn, user_id, bankcard_id, phone_no, amount, actual_amount, fee)

    return result


def _withdraw_failed():
    flash(u"提现失败，请核实账户信息！", category="error")
    return redirect(url_for('.withdraw'))


def _withdraw_succeed(actual_amount, fee):
    success_message = u"提现 %s元, 手续费 %s元 申请成功！绿野将于3-5个工作日内审核并处理。" % (actual_amount, fee)
    flash(success_message, category="success")
    return redirect(url_for('main.index'))